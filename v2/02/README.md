# Exercice 2 - Le tier backend redémarre en boucle

| | |
|---|---|
| **Difficulté** | **... |
| **Durée indicative** | 15 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/02
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Une modification de la configuration nginx du tier backend a été livrée.
`helm upgrade` s'est terminé sans erreur, mais le déploiement ne se termine
jamais.

## Ce que vous devez constater

* `kubectl rollout status deploy/deployment-backend` ne rend pas la main
* un nouveau pod backend est en `CrashLoopBackOff`, avec un compteur de
  redémarrages qui augmente
* les anciens pods backend sont toujours `Running` et `Ready` : le site
  continue de répondre normalement

## Votre mission

Trouver ce qui empêche le conteneur de démarrer, et corriger le chart.

## Questions pour vous guider

* Le conteneur a-t-il démarre au moins une fois ? Ou lire ce qu'il a dit avant
  de mourir ?
* Quelle est la différence entre `kubectl logs <pod>` et
  `kubectl logs <pod> --previous` ?
* Quel objet du chart a été modifié par la livraison ? (`helm diff` ou
  `diff -ru` avec le dossier `00-initial`)
* Pourquoi le site répond-il encore, alors que la configuration livrée est
  cassée ? Que se passerait-il si un ancien pod redémarrait maintenant ?

## Critère de réussite

Tous les pods backend sont `Running 1/1` sans redémarrages, et
`kubectl rollout status deploy/deployment-backend` rend la main.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'après avoir trouvé, ou si vous êtes vraiment bloqué.*
