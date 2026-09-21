# Exercice 1 - Le deploiement ne se termine jamais

| | |
|---|---|
| **Difficulte** | *.... |
| **Duree indicative** | 10 min |

## Mise en place

```bash
cd v2/01
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Une mise a jour du tier frontend vient d'etre livree. `helm upgrade` s'est
termine sans erreur, mais le deploiement ne se termine jamais et la commande
`kubectl rollout status` reste bloquee.

## Ce que vous devez constater

* `kubectl rollout status deploy/deployment-frontend` ne rend pas la main
* de nouveaux pods frontend apparaissent, mais ne demarrent pas
* le site continue pourtant de repondre

## Votre mission

Identifier pourquoi les nouveaux pods ne demarrent pas, et corriger le chart.

## Questions pour vous guider

* Dans quel etat sont les nouveaux pods ? Depuis combien de temps ?
* Ou trouve-t-on la raison exacte pour laquelle un conteneur ne demarre pas,
  quand il n'a jamais demarre ? (indice : ce n'est pas `kubectl logs`)
* Pourquoi le site repond-il encore alors que les nouveaux pods sont en echec ?

## Critere de reussite

`kubectl get pods -l tier=frontend` montre uniquement des pods `Running 1/1`,
et `kubectl rollout status deploy/deployment-frontend` rend la main.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'apres avoir trouve, ou si vous etes vraiment bloque.*
