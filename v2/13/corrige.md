# Corrige - exercice 13 : Elasticsearch passe en lecture seule

| | |
|---|---|
| **Panne** | volume d'Elasticsearch reduit a `128Mi`, sous le seuil `flood_stage` de 128 mb |
| **Fichier(s) modifie(s)** | `values.yaml` |
| **Symptome attendu** | cluster `green` mais index en lecture seule, erreurs 429 dans les Jobs |

> A ne pas distribuer aux etudiants avant la fin de l'exercice.

## La panne injectee

`values.yaml` :

```diff
   elasticsearch:
-    size: 2Gi
+    size: 128Mi
```

Le chart configure des seuils de disque en valeurs absolues
(`configmap-elasticsearch`) :

```yaml
  cluster.routing.allocation.disk.watermark.low:        "512mb"
  cluster.routing.allocation.disk.watermark.high:       "256mb"
  cluster.routing.allocation.disk.watermark.flood_stage: "128mb"
```

Sur un volume de 128 Mi, l'espace libre est inferieur a 128 mb des le
demarrage : le seuil `flood_stage` est franchi et Elasticsearch place tous les
index du noeud en **lecture seule**.

## Demarche de diagnostic

```bash
kubectl -n <ns> logs -l tier=report --tail=-1 | tail -20
# curl: (22) The requested URL returned error: 429
```

Le detail se lit dans les logs d'Elasticsearch et en rejouant la requete :

```bash
kubectl -n <ns> logs statefulset-elasticsearch-0 | grep -i flood
# flood stage disk watermark [128mb] exceeded on [...][statefulset-elasticsearch-0]
#   free: 96.4mb[75.3%], all indices on this node will be marked read-only

kubectl -n <ns> exec statefulset-elasticsearch-0 -- df -h /usr/share/elasticsearch/data
# Filesystem  Size  Used Avail Use% Mounted on
# /dev/...    122M   14M   96M  13% /usr/share/elasticsearch/data
```

Le point important : **le cluster est `green`**. Le vert dit que tous les
shards sont alloues, pas que l'on peut ecrire. Un blocage `read_only_allow_delete`
n'apparait pas dans `_cluster/health`, mais dans les erreurs 429 des clients.

## Correction

1. Agrandir le PVC. La StorageClass doit autoriser l'extension :

```bash
kubectl get sc <classe> -o jsonpath='{.allowVolumeExpansion}{"\n"}'
kubectl -n <ns> patch pvc data-statefulset-elasticsearch-0 \
  -p '{"spec":{"resources":{"requests":{"storage":"2Gi"}}}}'
kubectl -n <ns> get pvc data-statefulset-elasticsearch-0 -w
```

2. Remettre `size: 2Gi` dans `values.yaml`... et constater que `helm upgrade`
   echoue :

```
Forbidden: updates to statefulset spec for fields other than 'replicas',
'ordinals', 'template', 'updateStrategy', 'persistentVolumeClaimRetentionPolicy'
and 'minReadySeconds' are forbidden
```

`volumeClaimTemplates` est **immuable**. Il faut supprimer l'objet StatefulSet
en laissant vivre ses pods et son PVC, puis laisser Helm le recreer :

```bash
kubectl -n <ns> delete statefulset statefulset-elasticsearch --cascade=orphan
helm upgrade --install monchart . -n <ns>
```

3. Le blocage `read_only_allow_delete` est leve automatiquement par
   Elasticsearch des que l'espace libre repasse au-dessus du seuil `high`
   (verification toutes les 30 s). Pour forcer :

```bash
kubectl -n <ns> exec statefulset-elasticsearch-0 -- \
  curl -s -XPUT 'http://localhost:9200/_all/_settings' \
  -H 'Content-Type: application/json' \
  -d '{"index.blocks.read_only_allow_delete": null}'
```

## Rappel theorique

* Trois seuils de disque : `low` (plus d'allocation de nouveaux shards),
  `high` (deplacement des shards), `flood_stage` (index en lecture seule).
  Exprimables en pourcentage ou en valeur absolue d'espace **libre**.
* Depuis la 7.4, le blocage de `flood_stage` est leve automatiquement.
* `volumeClaimTemplates` immuable : c'est LA difficulte des StatefulSet.
  La sequence est toujours : agrandir le ou les PVC a la main, puis
  `delete sts --cascade=orphan` et recreer. Les pods ne sont pas interrompus.
* Corollaire : mieux vaut dimensionner genereusement un volume de StatefulSet
  des le depart, ou utiliser une classe qui autorise l'extension.

---

*Retour a l'etat sain : `diff -ru ../00-initial ../13` montre exactement
ce qui a ete modifie.*
