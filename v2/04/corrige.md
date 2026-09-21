# Corrige - exercice 4 : Des pods qui restent en Pending

| | |
|---|---|
| **Panne** | `frontend.resources.requests.memory` passe a `64Gi` |
| **Fichier(s) modifie(s)** | `values.yaml` |
| **Symptome attendu** | nouveaux pods frontend en `Pending`, jamais planifies |

> A ne pas distribuer aux etudiants avant la fin de l'exercice.

## La panne injectee

`values.yaml`, tier frontend :

```diff
   resources:
     requests:
-      memory: "32M"
+      memory: "64Gi"
```

## Demarche de diagnostic

```bash
kubectl -n <ns> get pods -l tier=frontend
# NAME                                   READY   STATUS    RESTARTS   AGE
# deployment-frontend-5b7c96f4d-9xqzt    0/1     Pending   0          2m

kubectl -n <ns> describe pod -l tier=frontend | tail -5
#   Warning  FailedScheduling  ... 0/3 nodes are available: 3 Insufficient memory.
```

C'est le **scheduler** qui bloque : il additionne les `requests` de tous les
pods deja places sur un noeud et refuse d'en ajouter un qui ne tient pas. La
memoire reellement utilisee n'entre pas en ligne de compte, seules les
`requests` comptent.

```bash
kubectl describe node <noeud> | grep -A6 'Allocatable'
kubectl describe node <noeud> | grep -A8 'Allocated resources'
```

## Correction

Retablir `memory: "32M"` dans les `requests` du frontend, puis `helm upgrade`.

## Rappel theorique

* `requests` = ce qui est **reserve** : sert au placement et au calcul de la
  classe de QoS. `limits` = le **plafond** : sert a l'eviction (memoire) ou au
  throttling (CPU).
* `Pending` = probleme de placement (ressources, `nodeSelector`, taints,
  affinites, volume non disponible). Le detail est toujours dans les evenements.
* `requests` trop hautes : gachis de capacite et pods non planifiables.
  `requests` trop basses : surreservation et evictions sous charge.

---

*Retour a l'etat sain : `diff -ru ../00-initial ../04` montre exactement
ce qui a ete modifie.*
