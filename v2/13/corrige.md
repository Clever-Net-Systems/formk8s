# Corrigé - exercice 13 : Elasticsearch passe en lecture seule

| | |
|---|---|
| **Panne** | volume d'Elasticsearch réduit à `128Mi`, sous le seuil `flood_stage` de 128 mb |
| **Fichier(s) modifié(s)** | `values.yaml` |
| **Symptôme attendu** | cluster `green` mais index en lecture seule, erreurs 429 dans les Jobs |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

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

Sur un volume de 128 Mi, l'espace libre est inférieur à 128 mb dès le
démarrage : le seuil `flood_stage` est franchi et Elasticsearch place tous les
index du noeud en **lecture seule**.

## Démarche de diagnostic

```bash
kubectl -n <ns> logs -l tier=report --tail=-1 | tail -20
# curl: (22) The requested URL returned error: 429
```

Le détail se lit dans les logs d'Elasticsearch et en rejouant la requête :

```bash
kubectl -n <ns> logs statefulset-elasticsearch-0 | grep -i flood
# flood stage disk watermark [128mb] exceeded on [...][statefulset-elasticsearch-0]
#   free: 96.4mb[75.3%], all indices on this node will be marked read-only

kubectl -n <ns> exec statefulset-elasticsearch-0 -- df -h /usr/share/elasticsearch/data
# Filesystem  Size  Used Avail Use% Mounted on
# /dev/...    122M   14M   96M  13% /usr/share/elasticsearch/data
```

Le point important : **le cluster est `green`**. Le vert dit que tous les
shards sont alloués, pas que l'on peut écrire. Un blocage
`read_only_allow_delete`
n'apparaît pas dans `_cluster/health`, mais dans les erreurs 429 des clients.

## Correction

1. Agrandir le PVC. La StorageClass doit autoriser l'extension :

```bash
kubectl get sc <classe> -o jsonpath='{.allowVolumeExpansion}{"\n"}'
kubectl -n <ns> patch pvc data-statefulset-elasticsearch-0 \
  -p '{"spec":{"resources":{"requests":{"storage":"2Gi"}}}}'
kubectl -n <ns> get pvc data-statefulset-elasticsearch-0 -w
```

2. Remettre `size: 2Gi` dans `values.yaml`... et constater que `helm upgrade`
   échoue :

```
Forbidden: updates to statefulset spec for fields other than 'replicas',
'ordinals', 'template', 'updateStrategy', 'persistentVolumeClaimRetentionPolicy'
and 'minReadySeconds' are forbidden
```

`volumeClaimTemplates` est **immuable**. Il faut supprimer l'objet StatefulSet
en laissant vivre ses pods et son PVC, puis laisser Helm le recréer :

```bash
kubectl -n <ns> delete statefulset statefulset-elasticsearch --cascade=orphan
helm upgrade --install monchart . -n <ns>
```

3. Le blocage `read_only_allow_delete` est levé automatiquement par
   Elasticsearch dès que l'espace libre repasse au-dessus du seuil `high`
   (vérification toutes les 30 s). Pour forcer :

```bash
kubectl -n <ns> exec statefulset-elasticsearch-0 -- \
  curl -s -XPUT 'http://localhost:9200/_all/_settings' \
  -H 'Content-Type: application/json' \
  -d '{"index.blocks.read_only_allow_delete": null}'
```

## Rappel théorique

* Trois seuils de disque : `low` (plus d'allocation de nouveaux shards),
  `high` (déplacement des shards), `flood_stage` (index en lecture seule).
  Exprimables en pourcentage ou en valeur absolue d'espace **libre**.
* Depuis la 7.4, le blocage de `flood_stage` est levé automatiquement.
* `volumeClaimTemplates` immuable : c'est LA difficulté des StatefulSet.
  La séquence est toujours : agrandir le ou les PVC à la main, puis
  `delete sts --cascade=orphan` et recréer. Les pods ne sont pas interrompus.
* Corollaire : mieux vaut dimensionner généreusement un volume de StatefulSet
  des le départ, ou utiliser une classe qui autorise l'extension.

---

*Retour à l'état sain : `diff -ru ../00-initial ../13` montre exactement
ce qui a été modifié.*
