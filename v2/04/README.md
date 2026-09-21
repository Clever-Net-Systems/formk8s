# Exercice 4 - Des pods qui restent en Pending

| | |
|---|---|
| **Difficulté** | *.... |
| **Durée indicative** | 10 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/04
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Après une revue de capacité, quelqu'un a "ajusté" les ressources demandées par
le tier frontend. Depuis, la mise à jour ne passe plus.

## Ce que vous devez constater

* les nouveaux pods frontend restent en `Pending`, indéfiniment
* aucun conteneur n'est créé, il n'y a rien dans les logs
* les anciens pods continuent de servir le trafic

## Votre mission

Expliquer pourquoi le planificateur refuse de placer ces pods, et corriger.

## Questions pour vous guider

* Un pod `Pending`, c'est un pod qui n'a pas encore de noeud. Qui décide, et
  ou explique-t-il son refus ?
* `kubectl describe pod <pod>` : que dit la dernière ligne des événements ?
* Combien de mémoire vos noeuds ont-ils réellement ?
  `kubectl describe node <noeud> | grep -A6 Allocatable`
* Quelle différence entre `requests` et `limits` pour le placement d'un pod ?

## Critère de réussite

Tous les pods frontend sont `Running`, et le rollout se termine.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'après avoir trouvé, ou si vous êtes vraiment bloqué.*
