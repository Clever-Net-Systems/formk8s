# Corrige - exercice 9 : Plus aucun rapport depuis ce matin

| | |
|---|---|
| **Panne** | `reportCronJob.indexName` passe a `Formation-Reports` : Elasticsearch refuse les majuscules |
| **Fichier(s) modifie(s)** | `values.yaml` |
| **Symptome attendu** | tous les Jobs du CronJob en echec, plus aucun rapport ecrit |

> A ne pas distribuer aux etudiants avant la fin de l'exercice.

## La panne injectee

`values.yaml` :

```diff
-  indexName: "formation-reports"
+  indexName: "Formation-Reports"
```

Elasticsearch **refuse les noms d'index contenant des majuscules**.

## Demarche de diagnostic

```bash
kubectl -n <ns> get cronjob,jobs -l tier=report
# cronjob.batch/cronjob-report   */1 * * * *   False   0   42s
# job.batch/cronjob-report-29833398   Complete   1/1
# job.batch/cronjob-report-29833401   Failed     0/1      <- les recents echouent

kubectl -n <ns> logs -l tier=report --tail=-1 | tail -15
# -> creation de l'index Formation-Reports
# curl: (22) The requested URL returned error: 400
```

Pour le detail, on rejoue la requete a la main :

```bash
kubectl -n <ns> run curl-test --rm -it --restart=Never --image=curlimages/curl:8.11.1 \
  --overrides='{"spec":{"securityContext":{"runAsNonRoot":true,"runAsUser":65534,"seccompProfile":{"type":"RuntimeDefault"}},"containers":[{"name":"curl-test","image":"curlimages/curl:8.11.1","securityContext":{"allowPrivilegeEscalation":false,"capabilities":{"drop":["ALL"]}},"args":["-s","-XPUT","http://service-elasticsearch:9200/Formation-Reports"]}]}}'
# {"error":{"type":"invalid_index_name_exception",
#   "reason":"Invalid index name [Formation-Reports], must be lowercase"},"status":400}
```

Le rapport n'est pas ecrit parce que le script s'arrete a la creation de
l'index (`set -e` + `curl --fail`), donc **avant** l'ecriture sur le volume.

L'historique conserve est pilote par le chart :
`successfulJobsHistoryLimit: 3` et `failedJobsHistoryLimit: 3`. C'est ce qui
permet de voir cote a cote les derniers Jobs reussis et les derniers echoues.
Les pods des Jobs termines ne sont pas supprimes : leurs logs restent lisibles.

## Correction

Retablir `indexName: "formation-reports"`, puis `helm upgrade`. Un CronJob
n'est pas "redemarre" : la prochaine occurrence, a la minute suivante, utilisera
la nouvelle definition. Pour ne pas attendre :

```bash
kubectl -n <ns> create job --from=cronjob/cronjob-report verif-1
kubectl -n <ns> logs job/verif-1
```

## Rappel theorique

* Hierarchie : CronJob -> Job -> Pod. Un Job en echec ne "reessaie" que dans la
  limite de son `backoffLimit` (0 ici : c'est le cron qui rejoue chaque minute).
* `concurrencyPolicy: Forbid` empeche deux executions simultanees ;
  `startingDeadlineSeconds` abandonne une occurrence trop en retard.
* Regles de nommage Elasticsearch : minuscules, pas de `\ / * ? " < > |`,
  pas de nom commencant par `-`, `_` ou `+`.

---

*Retour a l'etat sain : `diff -ru ../00-initial ../09` montre exactement
ce qui a ete modifie.*
