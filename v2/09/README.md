# Exercice 9 - Plus aucun rapport depuis ce matin

| | |
|---|---|
| **Difficulte** | ***.. |
| **Duree indicative** | 20 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/09
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Le tableau de bord affiche `rapport du CronJob : PERIME`. Le dernier fichier
present sur le volume partage date d'avant la derniere mise a jour.
Les tiers frontend, backend et Elasticsearch sont pourtant tous en bonne sante.

## Ce que vous devez constater

* les rapports ne sont plus mis a jour (`kubectl port-forward
  svc/service-backend-clusterip 8080:80` puis `http://localhost:8080/reports/`)
* des Jobs en echec s'accumulent

## Votre mission

Retrouver la cause exacte de l'echec, la corriger, et verifier qu'un nouveau
rapport est bien ecrit.

## Questions pour vous guider

* Un CronJob cree des Jobs, qui creent des Pods. A quel etage est le probleme ?
  `kubectl get cronjob,jobs,pods -l tier=report`
* Combien de Jobs en echec sont conserves ? Et combien de Jobs reussis ?
  Qu'est-ce qui pilote cela dans le chart ?
* Comment lire les logs d'un Job deja termine ?
* Le message d'erreur vient-il du script, ou du serveur qu'il interroge ?
* Pourquoi le rapport n'est-il meme pas ecrit sur le volume, alors que l'erreur
  concerne Elasticsearch ? (lisez le script dans `configmap-report-script`)

## Critere de reussite

Un nouveau fichier `report-*.txt` apparait dans la minute, les Jobs repassent
en `Complete`, et la pastille du tableau de bord redevient verte.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'apres avoir trouve, ou si vous etes vraiment bloque.*
