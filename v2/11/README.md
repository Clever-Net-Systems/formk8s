# Exercice 11 - Des pods evinces les uns apres les autres

| | |
|---|---|
| **Difficulte** | ****. |
| **Duree indicative** | 15 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/11
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Une revue de capacite a fait passer le stockage ephemere du tier frontend a une
valeur plus "raisonnable". Depuis, la mise a jour ne se termine pas et des pods
morts s'accumulent dans le namespace.

## Ce que vous devez constater

* de nouveaux pods frontend apparaissent, puis passent en `Evicted` au bout de
  quelques dizaines de secondes
* la liste des pods s'allonge a chaque minute
* le site continue de repondre (les anciens pods tiennent bon)

## Votre mission

Comprendre qui evince ces pods et pourquoi, puis corriger.

## Questions pour vous guider

* `kubectl describe pod <un pod Evicted>` : quel est le message exact ?
* Qu'est-ce que le "stockage ephemere" d'un pod, concretement ? Qu'est-ce qui
  est compte dedans, et qu'est-ce qui ne l'est pas ?
* Le volume `pvc-reports` est-il concerne ?
* Quelle difference entre un pod `Evicted` et un conteneur `OOMKilled` ?
* Comment nettoyer les pods `Evicted` une fois la panne corrigee ?

## Critere de reussite

Le rollout se termine, il n'y a plus que des pods `Running`, et plus aucun pod
`Evicted` ne reapparait.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'apres avoir trouve, ou si vous etes vraiment bloque.*
