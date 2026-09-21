# Exercice 2 - Le tier backend redemarre en boucle

| | |
|---|---|
| **Difficulte** | **... |
| **Duree indicative** | 15 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/02
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Une modification de la configuration nginx du tier backend a ete livree.
Depuis, plus rien ne repond du cote backend, et la page d'accueil du frontend
affiche `backend : injoignable`.

## Ce que vous devez constater

* les pods backend sont en `CrashLoopBackOff`, avec un compteur de redemarrages
  qui augmente
* le tier frontend, lui, va bien

## Votre mission

Trouver ce qui empeche le conteneur de demarrer, et corriger le chart.

## Questions pour vous guider

* Le conteneur a-t-il demarre au moins une fois ? Ou lire ce qu'il a dit avant
  de mourir ?
* Quelle est la difference entre `kubectl logs <pod>` et
  `kubectl logs <pod> --previous` ?
* Quel objet du chart a ete modifie par la livraison ? (`helm diff` ou
  `git diff` avec le dossier `initial`)

## Critere de reussite

Les pods backend sont `Running 1/1` sans redemarrages, et la page du frontend
repasse au vert.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'apres avoir trouve, ou si vous etes vraiment bloque.*
