# Exercice 8 - La configuration a changé, l'application non

| | |
|---|---|
| **Difficulté** | ***.. |
| **Durée indicative** | 15 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/08
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Le numéro d'application (`APPID`) doit passer de 42 à 99. La valeur a été
changée dans `values.yaml` et `helm upgrade` s'est bien déroulé.

Pourtant l'application continue d'utiliser 42.

## Ce que vous devez constater

```bash
kubectl -n <prenom>-tshoot get cm configmap-myapp -o jsonpath='{.data.APPID}'
kubectl -n <prenom>-tshoot exec deploy/deployment-frontend -- env | grep APPID
```

Les deux ne disent pas la même chose.

## Votre mission

Expliquer pourquoi, faire prendre en compte la nouvelle valeur, puis rendre le
chart durablement correct pour que le problème ne se reproduise pas.

## Questions pour vous guider

* Depuis quand les pods tournent-ils ? (`kubectl get pods`) Ont-ils redémarre
  pendant le `helm upgrade` ?
* Comment `APPID` arrive-t-il dans le conteneur : variable d'environnement ou
  fichier monté ? Cela change-t-il quelque chose ?
* Comparez avec le comportement des ConfigMap `configmap-frontend` et
  `configmap-backend` : pourquoi ceux-la font-ils redémarrer les pods quand on
  les modifie ? Regardez les annotations du Deployment.
* Quelle commande permet de forcer un redémarrage propre, sans supprimer de pod
  à la main ?

## Critère de réussite

`kubectl exec deploy/deployment-frontend -- env | grep APPID` renvoie 99, et
une modification ultérieure de `appId` est prise en compte automatiquement.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'après avoir trouvé, ou si vous êtes vraiment bloqué.*
