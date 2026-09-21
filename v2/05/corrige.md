# Corrigé - exercice 5 : Elasticsearch ne démarre plus après un ajustement de mémoire

| | |
|---|---|
| **Panne** | `elasticsearch.resources.limits.memory` passé à `512Mi`, sous la taille du tas JVM |
| **Fichier(s) modifié(s)** | `values.yaml` |
| **Symptôme attendu** | `statefulset-elasticsearch-0` tué par le noyau : `OOMKilled`, code 137 |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

`values.yaml`, tier elasticsearch :

```diff
     limits:
-      memory: "1536Mi"
+      memory: "512Mi"
```

Le tas de la JVM est fixé à `-Xms512m -Xmx512m` : à lui seul il remplit déjà la
limite du conteneur, sans compter le hors-heap (metaspace, buffers réseau,
Lucene, threads). Le noyau tue donc le processus dès le démarrage.

## Démarche de diagnostic

```bash
kubectl -n <ns> get pod statefulset-elasticsearch-0
# READY   STATUS             RESTARTS
# 0/1     CrashLoopBackOff   3 (20s ago)

kubectl -n <ns> logs statefulset-elasticsearch-0 --previous
# (rien, ou un démarrage de JVM interrompu net)

kubectl -n <ns> describe pod statefulset-elasticsearch-0 | grep -A6 'Last State'
#     Last State:     Terminated
#       Reason:       OOMKilled
#       Exit Code:    137
```

C'est le signe distinctif : **quand le noyau tue un processus, il ne laisse pas
de message applicatif**. Les logs sont muets, seul `describe` parle. Le code 137
= 128 + 9 (SIGKILL).

## Correction

Rétablir `memory: "1536Mi"` dans les `limits` d'Elasticsearch.

L'autre correction possible serait de baisser le tas
(`javaOpts: "-Xms256m -Xmx256m"`) pour tenir dans 512 Mi. Elle est mauvaise
ici : 256 Mo de tas sont trop justes pour Elasticsearch, on déplacerait le
problème vers des GC permanents et des erreurs `circuit_breaking_exception`.

## Rappel théorique

* `OOMKilled` vient du **cgroup** du conteneur : le processus a dépassé
  `limits.memory`. Ce n'est pas l'OOM killer global de la machine.
* Règle pour une JVM en conteneur : tas <= 50 % de la limite ; ici un tiers.
* La mémoire n'est pas compressible : dépassement = mort immédiate. Le CPU, lui,
  est simplement ralenti (throttling) quand on dépasse sa limite.
* Pour voir la consommation réelle : `kubectl top pod` (nécessite
  metrics-server).

---

*Retour à l'état sain : `diff -ru ../00-initial ../05` montre exactement
ce qui a été modifié.*
