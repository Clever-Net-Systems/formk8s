# Corrigé - exercice 2 : Le tier backend redémarre en boucle

| | |
|---|---|
| **Panne** | directive nginx `autoindex_on;` au lieu de `autoindex on;` |
| **Fichier(s) modifié(s)** | `templates/configmap-backend.yaml` |
| **Symptôme attendu** | pods backend en `CrashLoopBackOff` |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

`templates/configmap-backend.yaml`, bloc `location /reports/` :

```diff
-            autoindex on;
+            autoindex_on;
```

`autoindex_on` n'est pas une directive nginx : le processus refuse de démarrer.

## Démarche de diagnostic

```bash
kubectl -n <ns> get pods -l tier=backend
# NAME                                  READY   STATUS             RESTARTS
# deployment-backend-6c8f4d9b7-2xqzt    0/1     CrashLoopBackOff   4 (30s ago)   <- le nouveau
# deployment-backend-7d9c45b8f-4mrp5    1/1     Running            0             <- les anciens
# deployment-backend-7d9c45b8f-6ntcl    1/1     Running            0

kubectl -n <ns> logs deployment-backend-6c8f4d9b7-2xqzt --previous --tail=10
# nginx: [emerg] unknown directive "autoindex_on" in /etc/nginx/conf.d/default.conf:41
```

Le conteneur est mort : `kubectl logs` sans option affiche les logs du
conteneur *courant* (qui vient peut-être de redémarrer et n'a rien écrit).
`--previous` affiche ceux de l'instance précédente, celle qui a planté. On vise
le pod **par son nom** : avec `-l tier=backend`, la commande irait aussi
chercher les anciens pods, qui n'ont pas d'instance précédente.

**Pourquoi le site répond-il encore ?** Le Deployment est en `RollingUpdate`
avec `maxUnavailable: 25%` et `maxSurge: 25%`. Sur 2 replicas, Kubernetes
arrondit `maxUnavailable` **vers le bas** (0) et `maxSurge` **vers le haut**
(1) : il crée donc un pod supplémentaire et ne supprime aucun ancien tant que
le nouveau n'est pas `Ready`. Comme il ne le sera jamais, les deux anciens pods
continuent de servir et le rollout reste bloqué indéfiniment.

Attention au piège : les anciens pods montent le **même** ConfigMap, dont le
contenu a bien été mis à jour dans leur volume. S'ils redémarraient maintenant,
nginx relirait la configuration cassée et ils tomberaient à leur tour. Ils ne
survivent que parce que nginx ne relit pas sa configuration tout seul.

Le fichier est monté depuis le ConfigMap `configmap-backend` :

```bash
kubectl -n <ns> get cm configmap-backend -o jsonpath='{.data.default\.conf}' | grep -n autoindex
```

## Correction

Rétablir `autoindex on;` dans `templates/configmap-backend.yaml`, puis
`helm upgrade`. Les pods redémarrent tout seuls grâce à l'annotation
`checksum/configmap-backend` du Deployment.

## Rappel théorique

* `CrashLoopBackOff` n'est pas une erreur en soi : c'est kubelet qui espace les
  redémarrages (10 s, 20 s, 40 s... jusqu'à 5 min) d'un conteneur qui sort.
* Réflexe : `kubectl logs --previous`, puis `kubectl describe pod` pour le code
  de sortie (`Exit Code`) et la raison (`Reason`).
* Un conteneur qui sort en erreur immédiatement = problème de configuration ou
  de binaire ; un conteneur tué plus tard = plutôt une sonde ou une limite.
* Arrondis d'un `RollingUpdate` : `maxUnavailable` est arrondi vers le bas,
  `maxSurge` vers le haut. Avec 2 replicas et 25 %, cela donne 0 et 1 : une
  livraison cassée bloque le rollout **sans jamais couper le service**. C'est
  exactement ce que l'on attend d'un déploiement progressif.

---

*Retour à l'état sain : `diff -ru ../00-initial ../02` montre exactement
ce qui a été modifié.*
