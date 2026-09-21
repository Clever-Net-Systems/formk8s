# Corrigé - exercice 8 : La configuration a changé, l'application non

| | |
|---|---|
| **Panne** | aucune panne technique : `appId` modifié, mais aucune annotation `checksum/` ne couvre `configmap-myapp` |
| **Fichier(s) modifié(s)** | `values.yaml` |
| **Symptôme attendu** | le ConfigMap contient la nouvelle valeur, les pods l'ancienne |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

`values.yaml` :

```diff
-appId: 42
+appId: 99
```

Il n'y a en réalité aucun bug : c'est le **comportement normal** de Kubernetes,
et c'est un des pièges les plus fréquents en production.

## Démarche de diagnostic

```bash
kubectl -n <ns> get cm configmap-myapp -o jsonpath='{.data.APPID}{"\n"}'
# 99   <- le ConfigMap a bien été mis à jour

kubectl -n <ns> exec deploy/deployment-frontend -- env | grep APPID
# APPID=42   <- le pod, lui, n'a pas bouge

kubectl -n <ns> get pods -l tier=frontend
# AGE : 47m  -> aucun redemarrage pendant le helm upgrade
```

Les variables d'environnement sont injectées **au démarrage du conteneur** et
ne changent plus jamais ensuite. Modifier le ConfigMap ne touche pas les
processus déjà lancés.

(À noter : un ConfigMap monté en **volume** est, lui, mis à jour dans le pod au
bout d'une minute environ. Mais nginx ne relit pas sa configuration tout seul
pour autant : il faudrait lui envoyer un signal de rechargement.)

## Correction

Correction immédiate :

```bash
kubectl -n <ns> rollout restart deploy/deployment-frontend deploy/deployment-backend
```

Correction durable : ajouter au Deployment l'annotation qui existe déjà pour
les deux autres ConfigMap, dans `templates/deployment-frontend.yml` et
`templates/deployment-backend.yml` :

```yaml
      annotations:
        checksum/configmap-frontend: {{ include (print $.Template.BasePath "/configmap-frontend.yaml") . | sha256sum }}
        checksum/configmap-myapp: {{ include (print $.Template.BasePath "/configmap-myapp.yaml") . | sha256sum }}
```

L'empreinte du fichier change dès que son contenu change ; l'annotation du pod
template change donc aussi, et Helm déclenche un roulement des pods.

## Rappel théorique

* `envFrom`/`env` : figé au démarrage du conteneur.
* ConfigMap monté en volume : le contenu du fichier est rafraîchi (délai lié au
  `sync-period` de kubelet, ~1 min), mais l'application doit relire le fichier.
* `kubectl rollout restart` crée une nouvelle révision en modifiant une
  annotation du pod template : c'est un roulement propre, pas une suppression
  de pods.
* Un Secret suit exactement les mêmes règles.

---

*Retour à l'état sain : `diff -ru ../00-initial ../08` montre exactement
ce qui a été modifié.*
