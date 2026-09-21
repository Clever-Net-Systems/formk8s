# Exercice 12 - Volume partage sature

| | |
|---|---|
| **Difficulte** | ****. |
| **Duree indicative** | 20 min |
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

L'equipe data a livre un import de donnees (`job-import-dump`) qui depose un
fichier sur le volume partage. Depuis, le CronJob de rapport ne produit plus
rien et le tableau de bord affiche `rapport du CronJob : absent`.

## Ce que vous devez constater

* `job-import-dump` s'est termine normalement
* les Jobs `cronjob-report` echouent tous
* `/reports/` ne contient plus qu'un gros fichier (`kubectl port-forward
  svc/service-backend-clusterip 8080:80` puis `http://localhost:8080/reports/`)

## Votre mission

Retablir la production des rapports, puis proposer une correction durable.

## Questions pour vous guider

* Les logs d'un job de rapport en echec sont explicites : que disent-ils ?
  (regardez en particulier la sortie de `df`)
* Quelle est la taille du volume ? `kubectl get pvc pvc-reports`
* Deux corrections sont possibles : liberer de la place, ou agrandir le volume.
  Laquelle est immediate, laquelle est durable ?
* Un PVC peut-il etre agrandi a chaud ? Cela depend de quoi ?
  `kubectl get storageclass -o custom-columns=NAME:.metadata.name,EXPANSION:.allowVolumeExpansion`
* Peut-on, a l'inverse, reduire un PVC ?

## Critere de reussite

Un nouveau `report-*.txt` apparait dans la minute qui suit, et le tableau de
bord repasse au vert.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'apres avoir trouve, ou si vous etes vraiment bloque.*
