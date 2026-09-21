# Exercice 9 - Plus aucun rapport depuis ce matin

| | |
|---|---|
| **Difficulté** | **... |
| **Durée indicative** | 20 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/09
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Le tableau de bord affiche `rapport du CronJob : PERIME`. Le dernier fichier
présent sur le volume partagé date d'avant la dernière mise à jour.
Les tiers frontend, backend et Elasticsearch sont pourtant tous en bonne santé.

## Ce que vous devez constater

* des Jobs en échec s'accumulent
* les rapports ne sont plus mis à jour (`kubectl port-forward
  svc/service-backend-clusterip 8080:80` puis `http://localhost:8080/reports/`)
* sur la page du frontend, la pastille du rapport reste verte pendant les deux
  premières minutes, puis passe au rouge (`PERIME`) : le tableau de bord tolère
  une exécution manquée avant de signaler la panne

## Votre mission

Retrouver la cause exacte de l'échec, la corriger, et vérifier qu'un nouveau
rapport est bien écrit.

## Questions pour vous guider

* Un CronJob crée des Jobs, qui créent des Pods. À quel étage est le problème ?
  `kubectl get cronjob,jobs,pods -l tier=report`
* Combien de Jobs en échec sont conservés ? Et combien de Jobs réussis ?
  Qu'est-ce qui pilote cela dans le chart ?
* Comment lire les logs d'un Job déjà terminé ?
* Le message d'erreur est sans ambiguïté. Le fichier qu'il ne trouve pas, d'où
  vient-il ? Qu'est-ce qui le place dans le conteneur ?
* Quel est le nom réel de ce fichier, et où est-il défini dans le chart ?
* Pourquoi aucun rapport n'est écrit, alors que le volume partagé est
  parfaitement accessible ?

## Critère de réussite

Un nouveau fichier `report-*.txt` apparaît dans la minute, les Jobs repassent
en `Complete`, et la pastille du tableau de bord redevient verte.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'après avoir trouvé, ou si vous êtes vraiment bloqué.*
