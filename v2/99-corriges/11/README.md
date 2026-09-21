# Exercice 11 - Des pods évincés les uns après les autres

| | |
|---|---|
| **Difficulté** | ****. |
| **Durée indicative** | 15 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/11
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Une revue de capacité a fait passer le stockage éphémère du tier frontend à une
valeur plus "raisonnable". Depuis, la mise à jour ne se termine pas et des pods
morts s'accumulent dans le namespace.

## Ce que vous devez constater

* de nouveaux pods frontend apparaissent, vivent une quinzaine de secondes,
  puis passent en `Completed` sans jamais avoir été `Ready`
* la liste des pods s'allonge à chaque tentative
* le site continue de répondre (les anciens pods tiennent bon)

## Votre mission

Comprendre qui arrête ces pods et pourquoi, puis corriger.

## Questions pour vous guider

* Un pod géré par un Deployment qui affiche `Completed`, est-ce normal ? Que
  sont censés faire ses conteneurs ?
* Le statut du pod ne dit rien :
  `kubectl get pod <pod> -o custom-columns='PHASE:.status.phase,RAISON:.status.reason,MESSAGE:.status.message'`
  renvoie `Succeeded  <none>  <none>`. Où chercher, alors ?
* Regardez les **événements** : `kubectl describe pod <pod> | tail -10`.
  Qui parle, et que dit-il ?
* Qu'est-ce que le "stockage éphémère" d'un pod, concrètement ? Qu'est-ce qui
  est compté dedans, et qu'est-ce qui ne l'est pas ?
* Le volume `pvc-reports` est-il concerné ?
* Quelle différence entre un pod arrêté par kubelet et un conteneur `OOMKilled` ?
* Comment nettoyer ces pods morts une fois la panne corrigée ?

## Critère de réussite

Le rollout se termine, il n'y a plus que des pods `Running`, et plus aucun pod
`Evicted` ne réapparaît.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'après avoir trouvé, ou si vous êtes vraiment bloqué.*
