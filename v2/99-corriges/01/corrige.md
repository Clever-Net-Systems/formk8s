# Corrigé - exercice 1 : Le déploiement ne se termine jamais

| | |
|---|---|
| **Panne** | `frontend.image.tag` passé à `1.27-alpin` : ce tag n'existe pas |
| **Fichier(s) modifié(s)** | `values.yaml` |
| **Symptôme attendu** | nouveaux pods frontend en `ImagePullBackOff`, rollout bloqué |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

`values.yaml`, tier frontend :

```diff
-    tag: "1.27-alpine"
+    tag: "1.27-alpin"
```

Ce tag n'existe pas sur Docker Hub.

## Démarche de diagnostic

```bash
kubectl -n <ns> get pods -l tier=frontend
# NAME                                   READY   STATUS             RESTARTS
# deployment-frontend-6d4b9f8c7-x2k9p    0/1     ImagePullBackOff   0
```

`kubectl logs` ne sert à rien : le conteneur n'à jamais démarre, il n'y a
aucun log. L'information est dans les événements du pod :

```bash
kubectl -n <ns> describe pod -l tier=frontend | tail -20
#   Warning  Failed  ... Failed to pull image "nginxinc/nginx-unprivileged:1.27-alpin":
#            ... manifest unknown
```

Le site répond encore parce qu'un Deployment en `RollingUpdate` ne supprime les
anciens pods qu'une fois les nouveaux `Ready` : ici ils ne le sont jamais, donc
les anciens restent en place. C'est le comportement voulu, et c'est ce qui évite
qu'une mauvaise image mette la production à terre.

## Correction

Rétablir le tag dans `values.yaml` :

```yaml
    tag: "1.27-alpine"
```

puis `helm upgrade --install monchart . -n <ns>`.

## Rappel théorique

* `ErrImagePull` : l'échec vient de se produire. `ImagePullBackOff` : kubelet
  attend avant de réessayer (délai exponentiel jusqu'à 5 min).
* Les causes classiques : tag inexistant, faute de frappe sur le nom de
  l'image, registre privé sans `imagePullSecrets`, registre injoignable.
* `kubectl describe pod` (section Events) et `kubectl get events` sont les
  outils de diagnostic quand le conteneur n'à jamais démarre.

---

*Retour à l'état sain : `diff -ru ../../00-initial ../../01` montre exactement
ce qui a été modifié.*
