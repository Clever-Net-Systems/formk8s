# Corrige - exercice 1 : Le deploiement ne se termine jamais

| | |
|---|---|
| **Panne** | `frontend.image.tag` passe a `1.27-alpin` : ce tag n'existe pas |
| **Fichier(s) modifie(s)** | `values.yaml` |
| **Symptome attendu** | nouveaux pods frontend en `ImagePullBackOff`, rollout bloque |

> A ne pas distribuer aux etudiants avant la fin de l'exercice.

## La panne injectee

`values.yaml`, tier frontend :

```diff
-    tag: "1.27-alpine"
+    tag: "1.27-alpin"
```

Ce tag n'existe pas sur Docker Hub.

## Demarche de diagnostic

```bash
kubectl -n <ns> get pods -l tier=frontend
# NAME                                   READY   STATUS             RESTARTS
# deployment-frontend-6d4b9f8c7-x2k9p    0/1     ImagePullBackOff   0
```

`kubectl logs` ne sert a rien : le conteneur n'a jamais demarre, il n'y a
aucun log. L'information est dans les evenements du pod :

```bash
kubectl -n <ns> describe pod -l tier=frontend | tail -20
#   Warning  Failed  ... Failed to pull image "nginxinc/nginx-unprivileged:1.27-alpin":
#            ... manifest unknown
```

Le site repond encore parce qu'un Deployment en `RollingUpdate` ne supprime les
anciens pods qu'une fois les nouveaux `Ready` : ici ils ne le sont jamais, donc
les anciens restent en place. C'est le comportement voulu, et c'est ce qui evite
qu'une mauvaise image mette la production a terre.

## Correction

Retablir le tag dans `values.yaml` :

```yaml
    tag: "1.27-alpine"
```

puis `helm upgrade --install monchart . -n <ns>`.

## Rappel theorique

* `ErrImagePull` : l'echec vient de se produire. `ImagePullBackOff` : kubelet
  attend avant de reessayer (delai exponentiel jusqu'a 5 min).
* Les causes classiques : tag inexistant, faute de frappe sur le nom de
  l'image, registre prive sans `imagePullSecrets`, registre injoignable.
* `kubectl describe pod` (section Events) et `kubectl get events` sont les
  outils de diagnostic quand le conteneur n'a jamais demarre.

---

*Retour a l'etat sain : `diff -ru ../00-initial ../01` montre exactement
ce qui a ete modifie.*
