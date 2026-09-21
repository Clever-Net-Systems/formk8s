# Exercice 6 - Le backend est en bonne sante mais injoignable

| | |
|---|---|
| **Difficulte** | ***.. |
| **Duree indicative** | 15 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/06
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Le site affiche `backend : injoignable`. Pourtant les pods backend sont tous
`Running` et `Ready`, et ils repondent correctement quand on les interroge
directement.

## Ce que vous devez constater

* `kubectl get pods -l tier=backend` : tout est vert
* le frontend affiche une 503
* meme `kubectl port-forward svc/service-backend-clusterip 8080:80` refuse de
  s'ouvrir

## Votre mission

Expliquer pourquoi le trafic n'atteint pas les pods, et corriger.

## Questions pour vous guider

* Comment un Service sait-il a quels pods envoyer le trafic ?
* `kubectl get endpoints service-backend-clusterip` : que voyez-vous ?
* Comparez : `kubectl get svc service-backend-clusterip -o jsonpath='{.spec.selector}'`
  et `kubectl get pods -l tier=backend --show-labels`
* Testez un pod directement, sans passer par le Service :
  `kubectl exec deploy/deployment-frontend -- curl -s http://<IP_DU_POD>:8080/whoami`
* Que raconte exactement l'echec de `kubectl port-forward` sur ce Service ?

## Critere de reussite

`kubectl get endpoints service-backend-clusterip` liste les adresses des pods
backend, et le site repasse au vert.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'apres avoir trouve, ou si vous etes vraiment bloque.*
