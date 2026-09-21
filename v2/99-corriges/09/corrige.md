# Corrigé - exercice 9 : Plus aucun rapport depuis ce matin

| | |
|---|---|
| **Panne** | le CronJob lance `/scripts/rapport.sh`, alors que le script monté s'appelle `report.sh` |
| **Fichier(s) modifié(s)** | `templates/cronjob-report.yml` |
| **Symptôme attendu** | tous les Jobs du CronJob en échec, plus aucun rapport écrit |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

`templates/cronjob-report.yml` :

```diff
-              command: ["/bin/sh", "/scripts/report.sh"]
+              command: ["/bin/sh", "/scripts/rapport.sh"]
```

Le conteneur reçoit l'ordre d'exécuter un fichier qui n'existe pas.

## Démarche de diagnostic

On descend la hiérarchie CronJob -> Job -> Pod :

```bash
kubectl -n <ns> get cronjob,jobs -l tier=report
# cronjob.batch/cronjob-report        */1 * * * *   False   0   42s
# job.batch/cronjob-report-29833398   Complete   1/1        <- les anciens
# job.batch/cronjob-report-29833401   Failed     0/1        <- depuis la livraison
# job.batch/cronjob-report-29833402   Failed     0/1
```

Les logs du dernier Job en échec suffisent :

```bash
kubectl -n <ns> logs -l tier=report --tail=-1 | tail -5
# /bin/sh: can't open '/scripts/rapport.sh': No such file or directory
```

Reste à savoir d'où vient `/scripts`. C'est un volume du CronJob, alimenté par
un ConfigMap :

```bash
kubectl -n <ns> get cronjob cronjob-report \
  -o jsonpath='{.spec.jobTemplate.spec.template.spec.volumes}{"\n"}'
# [{"configMap":{"defaultMode":365,"name":"configmap-report-script"},"name":"scripts"} ...
```

Et le ConfigMap ne contient qu'une clé, qui donne son nom au fichier :

```bash
kubectl -n <ns> get cm configmap-report-script -o jsonpath='{.data}' | head -c 40
# {"report.sh":"#!/bin/sh\n# Chaque minute :
```

Le fichier s'appelle donc `report.sh`, pas `rapport.sh`. Aucun rapport n'est
écrit parce que le script ne démarre même pas : le volume partagé, lui, n'a
jamais été en cause.

## Correction

Rétablir le chemin dans `templates/cronjob-report.yml` :

```yaml
              command: ["/bin/sh", "/scripts/report.sh"]
```

puis `helm upgrade`. Un CronJob n'est pas "redémarré" : la prochaine occurrence,
à la minute suivante, utilisera la nouvelle définition. Pour ne pas attendre :

```bash
kubectl -n <ns> create job --from=cronjob/cronjob-report verif-1
kubectl -n <ns> logs job/verif-1
```

## Rappel théorique

* Hiérarchie : CronJob -> Job -> Pod. Un Job en échec ne "réessaie" que dans la
  limite de son `backoffLimit` (0 ici : c'est le cron qui rejoue chaque minute).
* `concurrencyPolicy: Forbid` empêche deux exécutions simultanées ;
  `startingDeadlineSeconds` abandonne une occurrence trop en retard.
* Un ConfigMap monté en volume expose **une clé = un fichier**, et le nom du
  fichier est celui de la clé. Renommer la clé renomme le fichier dans tous les
  pods qui le montent.
* Les logs d'un pod terminé restent lisibles tant que le pod existe : ce sont
  `successfulJobsHistoryLimit` et `failedJobsHistoryLimit` qui décident combien
  de temps on peut encore les consulter.

---

*Retour à l'état sain : `diff -ru ../../00-initial ../../09` montre exactement
ce qui a été modifié.*
