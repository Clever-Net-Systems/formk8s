# Exercice 12 - Volume partagé saturé

| | |
|---|---|
| **Difficulté** | ****. |
| **Durée indicative** | 20 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
# Cet exercice change la taille d'un volume : un PVC ne peut pas retrecir,
# il faut donc repartir d'une installation neuve.
helm uninstall monchart -n <prenom>-tshoot
kubectl -n <prenom>-tshoot delete pvc --all

cd v2/12
helm install monchart . -n <prenom>-tshoot
```

## Contexte

L'équipe data a livré un import de données (`job-import-dump`) qui dépose un
fichier sur le volume partagé. Depuis, le CronJob de rapport ne produit rien
et le tableau de bord affiche `rapport du CronJob : absent`.

## Ce que vous devez constater

* `job-import-dump` s'est terminé normalement
* les Jobs `cronjob-report` échouent tous
* `/reports/` ne contient qu'un gros fichier (`kubectl port-forward
  svc/service-backend-clusterip 8080:80` puis `http://localhost:8080/reports/`)

## Votre mission

Rétablir la production des rapports, puis proposer une correction durable.

## Questions pour vous guider

* Les logs d'un job de rapport en échec sont explicites : que disent-ils ?
  (regardez en particulier la sortie de `df`)
* Quelle est la taille du volume ? `kubectl get pvc pvc-reports`
* Deux corrections sont possibles : libérer de la place, ou agrandir le volume.
  Laquelle est immédiate, laquelle est durable ?
* Un PVC peut-il être agrandi à chaud ? Cela dépend de quoi ?
  `kubectl get storageclass -o custom-columns=NAME:.metadata.name,EXPANSION:.allowVolumeExpansion`
* Peut-on, à l'inverse, réduire un PVC ?

## Critère de réussite

Un nouveau `report-*.txt` apparaît dans la minute qui suit, et le tableau de
bord repasse au vert.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'après avoir trouvé, ou si vous êtes vraiment bloqué.*
