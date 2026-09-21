# Exercice 10 - Un Job qui ne cree aucun pod

| | |
|---|---|
| **Difficulte** | ****. |
| **Duree indicative** | 15 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/10
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

L'equipe applicative a livre un Job de maintenance (`job-purge`) qui doit
nettoyer les vieux rapports sur le volume partage.

`helm upgrade` affiche `deployed`, le Job existe... mais il ne se passe
strictement rien. Aucun pod n'apparait, aucun log, aucun message d'erreur
visible.

## Ce que vous devez constater

* `kubectl get jobs` : `job-purge` existe, `COMPLETIONS 0/1`
* `kubectl get pods` : aucun pod de purge, nulle part
* `kubectl logs job/job-purge` : rien a lire

## Votre mission

Trouver ou est passe le pod, comprendre qui l'a refuse, et rendre le Job
deployable **sans affaiblir la securite du namespace**.

## Questions pour vous guider

* Si le pod n'existe pas, l'erreur ne peut pas etre sur le pod. Sur quel objet
  est-elle alors ? (`kubectl describe job job-purge`)
* Meme question avec `kubectl get events --sort-by=.lastTimestamp | tail -20`
* Quel est le niveau de Pod Security applique sur le namespace ?
  `kubectl get ns <prenom>-tshoot --show-labels`
* Comparez le `securityContext` de ce Job avec celui du CronJob
  `cronjob-report`, qui, lui, fonctionne. Qu'est-ce qui manque, exactement ?
* La commande `kubectl label ns ... pod-security.kubernetes.io/enforce=baseline`
  reglerait le probleme : pourquoi est-ce la mauvaise reponse ?

## Critere de reussite

`kubectl get jobs` affiche `job-purge 1/1`, et le namespace applique toujours
`enforce: restricted`.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'apres avoir trouve, ou si vous etes vraiment bloque.*
