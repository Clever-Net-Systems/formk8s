# Corrige - exercice 6 : Le backend est en bonne sante mais injoignable

| | |
|---|---|
| **Panne** | selecteur du Service backend passe a `tier: backends` |
| **Fichier(s) modifie(s)** | `templates/service-backend-clusterip.yml` |
| **Symptome attendu** | `endpoints service-backend-clusterip` vide, 503 sur le frontend |

> A ne pas distribuer aux etudiants avant la fin de l'exercice.

## La panne injectee

`templates/service-backend-clusterip.yml` :

```diff
   selector:
     app: MyApp
-    tier: backend
+    tier: backends
```

## Demarche de diagnostic

```bash
kubectl -n <ns> get endpoints service-backend-clusterip
# NAME                       ENDPOINTS   AGE
# service-backend-clusterip   <none>      1h
```

`<none>` est le symptome : le Service ne "voit" aucun pod. Un Service ne
connait pas les Deployments, il ne connait qu'un **selecteur de labels**.

`kubectl port-forward` echoue pour la meme raison, et le dit explicitement :
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

Retablir `tier: backend` dans le selecteur du Service, puis `helm upgrade`.
L'effet est immediat, sans redemarrage de pod : le controleur d'Endpoints
recalcule la liste en permanence.

## Rappel theorique

* Chaine complete : `Service.spec.selector` -> `EndpointSlice`/`Endpoints` ->
  regles kube-proxy sur chaque noeud -> pod.
* Un Endpoint n'apparait que si le pod correspond au selecteur **et** est
  `Ready` : un selecteur correct mais une readiness KO donne le meme `<none>`.
* Pourquoi avoir casse le selecteur du Service, et pas le label des pods ?
  Parce que `spec.selector` d'un Deployment est **immuable** : le modifier
  ferait echouer `helm upgrade` avec `field is immutable`, et on n'observerait
  pas la panne recherchee. C'est un piege classique : pour renommer un label de
  pods, il faut supprimer puis recreer le Deployment (voire
  `kubectl delete deploy --cascade=orphan`).
* Commande de reflexe : `kubectl get endpoints <svc>` avant toute autre chose.

---

*Retour a l'etat sain : `diff -ru ../00-initial ../06` montre exactement
ce qui a ete modifie.*
