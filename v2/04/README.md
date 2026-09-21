# Exercice 4 - Des pods qui restent en Pending

| | |
|---|---|
| **Difficulte** | *.... |
| **Duree indicative** | 10 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/04
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Apres une revue de capacite, quelqu'un a "ajuste" les ressources demandees par
le tier frontend. Depuis, la mise a jour ne passe plus.

## Ce que vous devez constater

* les nouveaux pods frontend restent en `Pending`, indefiniment
* aucun conteneur n'est cree, il n'y a rien dans les logs
* les anciens pods continuent de servir le trafic

## Votre mission

Expliquer pourquoi le planificateur refuse de placer ces pods, et corriger.

## Questions pour vous guider

* Un pod `Pending`, c'est un pod qui n'a pas encore de noeud. Qui decide, et
  ou explique-t-il son refus ?
* `kubectl describe pod <pod>` : que dit la derniere ligne des evenements ?
* Combien de memoire vos noeuds ont-ils reellement ?
  `kubectl describe node <noeud> | grep -A6 Allocatable`
* Quelle difference entre `requests` et `limits` pour le placement d'un pod ?

## Critere de reussite

Tous les pods frontend sont `Running`, et le rollout se termine.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'apres avoir trouve, ou si vous etes vraiment bloque.*
