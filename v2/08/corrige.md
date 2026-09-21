# Corrige - exercice 8 : La configuration a change, l'application non

| | |
|---|---|
| **Panne** | aucune panne technique : `appId` modifie, mais aucune annotation `checksum/` ne couvre `configmap-myapp` |
| **Fichier(s) modifie(s)** | `values.yaml` |
| **Symptome attendu** | le ConfigMap contient la nouvelle valeur, les pods l'ancienne |

> A ne pas distribuer aux etudiants avant la fin de l'exercice.

## La panne injectee

`values.yaml` :

```diff
-appId: 42
+appId: 99
```

Il n'y a en realite aucun bug : c'est le **comportement normal** de Kubernetes,
et c'est un des pieges les plus frequents en production.

## Demarche de diagnostic

```bash
kubectl -n <ns> get cm configmap-myapp -o jsonpath='{.data.APPID}{"\n"}'
# 99   <- le ConfigMap a bien ete mis a jour

kubectl -n <ns> exec deploy/deployment-frontend -- env | grep APPID
# APPID=42   <- le pod, lui, n'a pas bouge

kubectl -n <ns> get pods -l tier=frontend
# AGE : 47m  -> aucun redemarrage pendant le helm upgrade
```

Les variables d'environnement sont injectees **au demarrage du conteneur** et
ne changent plus jamais ensuite. Modifier le ConfigMap ne touche pas les
processus deja lances.

(A noter : un ConfigMap monte en **volume** est, lui, mis a jour dans le pod au
bout d'une minute environ. Mais nginx ne relit pas sa configuration tout seul
pour autant : il faudrait lui envoyer un signal de rechargement.)

## Correction

Correction immediate :

```bash
kubectl -n <ns> rollout restart deploy/deployment-frontend deploy/deployment-backend
```

Correction durable : ajouter au Deployment l'annotation qui existe deja pour
les deux autres ConfigMap, dans `templates/deployment-frontend.yml` et
`templates/deployment-backend.yml` :

```yaml
      annotations:
        checksum/configmap-frontend: {{ include (print $.Template.BasePath "/configmap-frontend.yaml") . | sha256sum }}
        checksum/configmap-myapp: {{ include (print $.Template.BasePath "/configmap-myapp.yaml") . | sha256sum }}
```

L'empreinte du fichier change des que son contenu change ; l'annotation du pod
template change donc aussi, et Helm declenche un roulement des pods.

## Rappel theorique

* `envFrom`/`env` : fige au demarrage du conteneur.
* ConfigMap monte en volume : le contenu du fichier est rafraichi (delai lie au
  `sync-period` de kubelet, ~1 min), mais l'application doit relire le fichier.
* `kubectl rollout restart` cree une nouvelle revision en modifiant une
  annotation du pod template : c'est un roulement propre, pas une suppression
  de pods.
* Un Secret suit exactement les memes regles.

---

*Retour a l'etat sain : `diff -ru ../00-initial ../08` montre exactement
ce qui a ete modifie.*
