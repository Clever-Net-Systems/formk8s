# Exercice 8 - La configuration a change, l'application non

| | |
|---|---|
| **Difficulte** | ***.. |
| **Duree indicative** | 15 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/08
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Le numero d'application (`APPID`) doit passer de 42 a 99. La valeur a ete
changee dans `values.yaml` et `helm upgrade` s'est bien deroule.

Pourtant l'application continue d'utiliser 42.

## Ce que vous devez constater

```bash
kubectl -n <prenom>-tshoot get cm configmap-myapp -o jsonpath='{.data.APPID}'
kubectl -n <prenom>-tshoot exec deploy/deployment-frontend -- env | grep APPID
```

Les deux ne disent pas la meme chose.

## Votre mission

Expliquer pourquoi, faire prendre en compte la nouvelle valeur, puis rendre le
chart durablement correct pour que le probleme ne se reproduise pas.

## Questions pour vous guider

* Depuis quand les pods tournent-ils ? (`kubectl get pods`) Ont-ils redemarre
  pendant le `helm upgrade` ?
* Comment `APPID` arrive-t-il dans le conteneur : variable d'environnement ou
  fichier monte ? Cela change-t-il quelque chose ?
* Comparez avec le comportement des ConfigMap `configmap-frontend` et
  `configmap-backend` : pourquoi ceux-la font-ils redemarrer les pods quand on
  les modifie ? Regardez les annotations du Deployment.
* Quelle commande permet de forcer un redemarrage propre, sans supprimer de pod
  a la main ?

## Critere de reussite

`kubectl exec deploy/deployment-frontend -- env | grep APPID` renvoie 99, et
une modification ulterieure de `appId` est prise en compte automatiquement.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'apres avoir trouve, ou si vous etes vraiment bloque.*
