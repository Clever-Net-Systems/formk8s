# Corrigé - exercice 9 : Plus aucun rapport depuis ce matin

| | |
|---|---|
| **Panne** | `reportCronJob.indexName` passé à `Formation-Reports` : Elasticsearch refuse les majuscules |
| **Fichier(s) modifié(s)** | `values.yaml` |
| **Symptôme attendu** | tous les Jobs du CronJob en échec, plus aucun rapport écrit |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

`values.yaml` :

```diff
-  indexName: "formation-reports"
+  indexName: "Formation-Reports"
```

Elasticsearch **refuse les noms d'index contenant des majuscules**.

## Démarche de diagnostic

```bash
kubectl -n <ns> get cronjob,jobs -l tier=report
# cronjob.batch/cronjob-report   */1 * * * *   False   0   42s
# job.batch/cronjob-report-29833398   Complete   1/1
# job.batch/cronjob-report-29833401   Failed     0/1      <- les recents echouent

kubectl -n <ns> logs -l tier=report --tail=-1 | tail -15
# -> creation de l'index Formation-Reports
# curl: (22) The requested URL returned error: 400
```

Pour le détail, on rejoue la requête à la main :

```bash
kubectl -n <ns> run curl-test --rm -it --restart=Never --image=curlimages/curl:8.11.1 \
  --overrides='{"spec":{"securityContext":{"runAsNonRoot":true,"runAsUser":65534,"seccompProfile":{"type":"RuntimeDefault"}},"containers":[{"name":"curl-test","image":"curlimages/curl:8.11.1","securityContext":{"allowPrivilegeEscalation":false,"capabilities":{"drop":["ALL"]}},"args":["-s","-XPUT","http://service-elasticsearch:9200/Formation-Reports"]}]}}'
# {"error":{"type":"invalid_index_name_exception",
#   "reason":"Invalid index name [Formation-Reports], must be lowercase"},"status":400}
```

Le rapport n'est pas écrit parce que le script s'arrête à la création de
l'index (`set -e` + `curl --fail`), donc **avant** l'écriture sur le volume.

L'historique conservé est piloté par le chart :
`successfulJobsHistoryLimit: 3` et `failedJobsHistoryLimit: 3`. C'est ce qui
permet de voir côté à côté les derniers Jobs réussis et les derniers échoués.
Les pods des Jobs terminés ne sont pas supprimés : leurs logs restent lisibles.

## Correction

Rétablir `indexName: "formation-reports"`, puis `helm upgrade`. Un CronJob
n'est pas "redémarre" : la prochaine occurrence, à la minute suivante, utilisera
la nouvelle définition. Pour ne pas attendre :

```bash
kubectl -n <ns> create job --from=cronjob/cronjob-report verif-1
kubectl -n <ns> logs job/verif-1
```

## Rappel théorique

* Hiérarchie : CronJob -> Job -> Pod. Un Job en échec ne "réessaie" que dans la
  limite de son `backoffLimit` (0 ici : c'est le cron qui rejoue chaque minute).
* `concurrencyPolicy: Forbid` empêche deux exécutions simultanées ;
  `startingDeadlineSeconds` abandonne une occurrence trop en retard.
* Règles de nommage Elasticsearch : minuscules, pas de `\ / * ? " < > |`,
  pas de nom commençant par `-`, `_` ou `+`.

---

*Retour à l'état sain : `diff -ru ../00-initial ../09` montre exactement
ce qui a été modifié.*
