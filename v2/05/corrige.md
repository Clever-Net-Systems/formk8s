# Corrige - exercice 5 : Elasticsearch ne demarre plus apres un ajustement de memoire

| | |
|---|---|
| **Panne** | `elasticsearch.resources.limits.memory` passe a `512Mi`, sous la taille du tas JVM |
| **Fichier(s) modifie(s)** | `values.yaml` |
| **Symptome attendu** | `statefulset-elasticsearch-0` tue par le noyau : `OOMKilled`, code 137 |

> A ne pas distribuer aux etudiants avant la fin de l'exercice.

## La panne injectee

`values.yaml`, tier elasticsearch :

```diff
     limits:
-      memory: "1536Mi"
+      memory: "512Mi"
```

Le tas de la JVM est fixe a `-Xms512m -Xmx512m` : a lui seul il remplit deja la
limite du conteneur, sans compter le hors-heap (metaspace, buffers reseau,
Lucene, threads). Le noyau tue donc le processus des le demarrage.

## Demarche de diagnostic

```bash
kubectl -n <ns> get pod statefulset-elasticsearch-0
# READY   STATUS             RESTARTS
# 0/1     CrashLoopBackOff   3 (20s ago)

kubectl -n <ns> logs statefulset-elasticsearch-0 --previous
# (rien, ou un demarrage de JVM interrompu net)

kubectl -n <ns> describe pod statefulset-elasticsearch-0 | grep -A6 'Last State'
#     Last State:     Terminated
#       Reason:       OOMKilled
#       Exit Code:    137
```

C'est le signe distinctif : **quand le noyau tue un processus, il ne laisse pas
de message applicatif**. Les logs sont muets, seul `describe` parle. Le code 137
= 128 + 9 (SIGKILL).

## Correction

Retablir `memory: "1536Mi"` dans les `limits` d'Elasticsearch.

L'autre correction possible serait de baisser le tas
(`javaOpts: "-Xms256m -Xmx256m"`) pour tenir dans 512 Mi. Elle est mauvaise
ici : 256 Mo de tas sont trop justes pour Elasticsearch, on deplacerait le
probleme vers des GC permanents et des erreurs `circuit_breaking_exception`.

## Rappel theorique

* `OOMKilled` vient du **cgroup** du conteneur : le processus a depasse
  `limits.memory`. Ce n'est pas l'OOM killer global de la machine.
* Regle pour une JVM en conteneur : tas <= 50 % de la limite ; ici un tiers.
* La memoire n'est pas compressible : depassement = mort immediate. Le CPU, lui,
  est simplement ralenti (throttling) quand on depasse sa limite.
* Pour voir la consommation reelle : `kubectl top pod` (necessite
  metrics-server).

---

*Retour a l'etat sain : `diff -ru ../00-initial ../05` montre exactement
ce qui a ete modifie.*
