# Corrigé - exercice 4 : Des pods qui restent en Pending

| | |
|---|---|
| **Panne** | `frontend.resources.requests.memory` passé à `64Gi` |
| **Fichier(s) modifié(s)** | `values.yaml` |
| **Symptôme attendu** | nouveaux pods frontend en `Pending`, jamais planifiés |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

`values.yaml`, tier frontend :

```diff
   resources:
     requests:
-      memory: "32M"
+      memory: "64Gi"
```

## Démarche de diagnostic

```bash
kubectl -n <ns> get pods -l tier=frontend
# NAME                                   READY   STATUS    RESTARTS   AGE
# deployment-frontend-5b7c96f4d-9xqzt    0/1     Pending   0          2m

kubectl -n <ns> describe pod -l tier=frontend | tail -5
#   Warning  FailedScheduling  ... 0/3 nodes are available: 3 Insufficient memory.
```

C'est le **scheduler** qui bloque : il additionne les `requests` de tous les
pods déjà placés sur un noeud et refuse d'en ajouter un qui ne tient pas. La
mémoire réellement utilisée n'entre pas en ligne de compte, seules les
`requests` comptent.

```bash
kubectl describe node <noeud> | grep -A6 'Allocatable'
kubectl describe node <noeud> | grep -A8 'Allocated resources'
```

## Correction

Rétablir `memory: "32M"` dans les `requests` du frontend, puis `helm upgrade`.

## Rappel théorique

* `requests` = ce qui est **réservé** : sert au placement et au calcul de la
  classe de QoS. `limits` = le **plafond** : sert à l'éviction (mémoire) ou au
  throttling (CPU).
* `Pending` = problème de placement (ressources, `nodeSelector`, taints,
  affinités, volume non disponible). Le détail est toujours dans les événements.
* `requests` trop hautes : gâchis de capacité et pods non planifiables.
  `requests` trop basses : surréservation et évictions sous charge.

---

*Retour à l'état sain : `diff -ru ../00-initial ../04` montre exactement
ce qui a été modifié.*
