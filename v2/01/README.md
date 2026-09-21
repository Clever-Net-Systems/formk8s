# Exercice 1 - Le déploiement ne se termine jamais

| | |
|---|---|
| **Difficulté** | *.... |
| **Durée indicative** | 10 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/01
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Une mise à jour du tier frontend vient d'être livrée, mais le déploiement ne se
termine jamais : `kubectl rollout status` reste bloquée.

## Ce que vous devez constater

* `kubectl rollout status deploy/deployment-frontend` ne rend pas la main
* de nouveaux pods frontend apparaissent, mais ne démarrent pas
* le site continue pourtant de répondre

## Votre mission

Identifier pourquoi les nouveaux pods ne démarrent pas, et corriger le chart.

## Questions pour vous guider

* Dans quel état sont les nouveaux pods ? Depuis combien de temps ?
* Où trouve-t-on la raison exacte pour laquelle un conteneur ne démarre pas,
  quand il n'à jamais démarre ? (indice : ce n'est pas `kubectl logs`)
* Pourquoi le site répond-il encore alors que les nouveaux pods sont en échec ?

## Critère de réussite

`kubectl get pods -l tier=frontend` montre uniquement des pods `Running 1/1`,
et `kubectl rollout status deploy/deployment-frontend` rend la main.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'après avoir trouvé, ou si vous êtes vraiment bloqué.*
