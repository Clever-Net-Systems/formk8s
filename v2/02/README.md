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
Depuis, plus rien ne répond du côté backend, et la page d'accueil du frontend
affiche `backend : injoignable`.

## Ce que vous devez constater

* les pods backend sont en `CrashLoopBackOff`, avec un compteur de redémarrages
  qui augmente
* le tier frontend, lui, va bien

## Votre mission

Trouver ce qui empêche le conteneur de démarrer, et corriger le chart.

## Questions pour vous guider

* Le conteneur a-t-il démarre au moins une fois ? Ou lire ce qu'il a dit avant
  de mourir ?
* Quelle est la différence entre `kubectl logs <pod>` et
  `kubectl logs <pod> --previous` ?
* Quel objet du chart a été modifié par la livraison ? (`helm diff` ou
  `git diff` avec le dossier `initial`)

## Critère de réussite

Les pods backend sont `Running 1/1` sans redémarrages, et la page du frontend
repasse au vert.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'après avoir trouvé, ou si vous êtes vraiment bloqué.*
