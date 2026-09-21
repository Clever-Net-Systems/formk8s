# Exercice 10 - Un Job qui ne crée aucun pod

| | |
|---|---|
| **Difficulté** | ****. |
| **Durée indicative** | 15 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/10
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

L'équipe applicative a livré un Job de maintenance (`job-purge`) qui doit
nettoyer les vieux rapports sur le volume partagé.

`helm upgrade` affiche `deployed`, le Job existe... mais il ne se passe
strictement rien. Aucun pod n'apparaît, aucun log, aucun message d'erreur
visible.

## Ce que vous devez constater

* `kubectl get jobs` : `job-purge` existe, `COMPLETIONS 0/1`
* `kubectl get pods` : aucun pod de purge, nulle part
* `kubectl logs job/job-purge` : rien à lire

## Votre mission

Trouver ou est passé le pod, comprendre qui l'a refusé, et rendre le Job
déployable **sans affaiblir la sécurité du namespace**.

## Questions pour vous guider

* Si le pod n'existe pas, l'erreur ne peut pas être sur le pod. Sur quel objet
  est-elle alors ? (`kubectl describe job job-purge`)
* Même question avec `kubectl get events --sort-by=.lastTimestamp | tail -20`
* Quel est le niveau de Pod Security appliqué sur le namespace ?
  `kubectl get ns <prenom>-tshoot --show-labels`
* Comparez le `securityContext` de ce Job avec celui du CronJob
  `cronjob-report`, qui, lui, fonctionne. Qu'est-ce qui manque, exactement ?
* La commande `kubectl label ns ... pod-security.kubernetes.io/enforce=baseline`
  réglerait le problème : pourquoi est-ce la mauvaise réponse ?

## Critère de réussite

`kubectl get jobs` affiche `job-purge 1/1`, et le namespace applique toujours
`enforce: restricted`.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'après avoir trouvé, ou si vous êtes vraiment bloqué.*
