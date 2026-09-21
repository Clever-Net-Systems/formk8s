# Corrigé - exercice 6 : Le backend est en bonne santé mais injoignable

| | |
|---|---|
| **Panne** | sélecteur du Service backend passé à `tier: backends` |
| **Fichier(s) modifié(s)** | `templates/service-backend-clusterip.yml` |
| **Symptôme attendu** | `endpoints service-backend-clusterip` vide, 503 sur le frontend |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

`templates/service-backend-clusterip.yml` :

```diff
   selector:
     app: MyApp
-    tier: backend
+    tier: backends
```

## Démarche de diagnostic

```bash
kubectl -n <ns> get endpoints service-backend-clusterip
# NAME                       ENDPOINTS   AGE
# service-backend-clusterip   <none>      1h
```

`<none>` est le symptôme : le Service ne "voit" aucun pod. Un Service ne
connaît pas les Deployments, il ne connaît qu'un **sélecteur de labels**.

`kubectl port-forward` échoue pour la même raison, et le dit explicitement :
`error: no selectable pods found for service`.

```bash
kubectl -n <ns> get svc service-backend-clusterip -o jsonpath='{.spec.selector}{"\n"}'
# {"app":"MyApp","tier":"backends"}
kubectl -n <ns> get pods -l tier=backend --show-labels
# ... app=MyApp,tier=backend,...
```

`backends` != `backend` : aucune correspondance, donc aucun Endpoint, donc
aucune destination pour le trafic.

## Correction

Rétablir `tier: backend` dans le sélecteur du Service, puis `helm upgrade`.
L'effet est immédiat, sans redémarrage de pod : le contrôleur d'Endpoints
recalcule la liste en permanence.

## Rappel théorique

* Chaîne complète : `Service.spec.selector` -> `EndpointSlice`/`Endpoints` ->
  règles kube-proxy sur chaque noeud -> pod.
* Un Endpoint n'apparaît que si le pod correspond au sélecteur **et** est
  `Ready` : un sélecteur correct mais une readiness KO donne le même `<none>`.
* Pourquoi avoir cassé le sélecteur du Service, et pas le label des pods ?
  Parce que `spec.selector` d'un Deployment est **immuable** : le modifier
  ferait échouer `helm upgrade` avec `field is immutable`, et on n'observerait
  pas la panne recherchée. C'est un piège classique : pour renommer un label de
  pods, il faut supprimer puis recréer le Deployment (voire
  `kubectl delete deploy --cascade=orphan`).
* Commande de réflexe : `kubectl get endpoints <svc>` avant toute autre chose.

---

*Retour à l'état sain : `diff -ru ../00-initial ../06` montre exactement
ce qui a été modifié.*
