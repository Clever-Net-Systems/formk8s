# Corrigé - exercice 13 : Elasticsearch passe en lecture seule

| | |
|---|---|
| **Panne** | un initContainer « restauration de snapshot » remplit le volume de données d'Elasticsearch, qui passe sous le seuil `flood_stage` |
| **Fichier(s) modifié(s)** | `templates/statefulset-elasticsearch.yml` |
| **Symptôme attendu** | Elasticsearch répond mais refuse les écritures (429) : les Jobs échouent, le rapport reste écrit |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

Ajout d'un initContainer dans `templates/statefulset-elasticsearch.yml`, qui
écrit sur le volume de données jusqu'à ne laisser que 80 Mo libres :

```yaml
              LIBRE=$(df -Pm "$DATA" | awk 'NR==2{print $4}')
              A_ECRIRE=$((LIBRE - LIBRE_CIBLE))
              dd if=/dev/zero of="$DATA/restore-snapshot.dump" bs=1M count="$A_ECRIRE"
```

Le volume fait 2 Gi, le seuil `flood_stage` du chart exige 128 Mo libres : avec
80 Mo restants, Elasticsearch place tous les index du nœud en **lecture seule**.

Le `spec.template` d'un StatefulSet étant modifiable, cette livraison passe
sans problème par `helm upgrade` — c'est justement le volume qui ne l'est pas,
et c'est tout l'objet de l'exercice.

## Démarche de diagnostic

```bash
kubectl -n <ns> get jobs -l tier=report
# job.batch/cronjob-report-29833401   Failed   0/1

kubectl -n <ns> logs -l tier=report --tail=-1 | tail -5
# curl: (22) The requested URL returned error: 429
```

Un 429 sur une écriture alors que le cluster répond aux lectures : ce n'est pas
une panne, c'est un **refus**. Elasticsearch le dit dans ses logs :

```bash
kubectl -n <ns> logs statefulset-elasticsearch-0 | grep -i flood | tail -2
# flood stage disk watermark [128mb] exceeded on [...][statefulset-elasticsearch-0]
#   free: 79.8mb[3.9%], all indices on this node will be marked read-only
```

Cette fois le disque est bien plein :

```bash
kubectl -n <ns> exec statefulset-elasticsearch-0 -- df -h /usr/share/elasticsearch/data
# Filesystem  Size  Used Avail Use% Mounted on
# /dev/...    2.0G  1.9G   80M   96% /usr/share/elasticsearch/data

kubectl -n <ns> exec statefulset-elasticsearch-0 -- ls -lh /usr/share/elasticsearch/data
# -rw-r--r--    1 elasticsearch elasticsearch   1.8G restore-snapshot.dump
# drwxrwxr-x    3 elasticsearch elasticsearch   4.0K nodes
```

Le coupable est identifié, et il est **légitime** : c'est le jeu de données
restauré. Le supprimer reviendrait à perdre la livraison. La seule solution est
donc d'agrandir le volume.

À noter : le cluster peut rester `green` tout du long. Le vert parle de
l'allocation des shards, pas des blocages d'écriture. Et le rapport continue
d'être écrit parce que le job écrit son fichier **avant** d'indexer son
document — c'est ce qui disculpe le volume partagé et le tier backend.

## Correction : agrandir le volume d'un StatefulSet

L'opération se fait en deux temps bien distincts : **rétablir le service**,
puis **remettre le chart en cohérence**. C'est la seconde partie qui est
pénible.

### Rétablir le service

Vérifier que la StorageClass autorise l'extension, puis agrandir le PVC :

```bash
kubectl get sc <classe> -o jsonpath='{.allowVolumeExpansion}{"\n"}'   # doit valoir true
kubectl -n <ns> patch pvc data-statefulset-elasticsearch-0 \
  -p '{"spec":{"resources":{"requests":{"storage":"4Gi"}}}}'
```

Ici le `kubectl patch` est **légitime**, contrairement à l'exercice 12 : ce PVC
n'est pas créé par Helm mais par le contrôleur du StatefulSet, à partir de
`volumeClaimTemplates`. Helm ne l'applique jamais, il ne peut donc pas y avoir
de conflit de propriétaire.

L'extension d'un volume **en cours d'utilisation** est stable depuis
Kubernetes 1.24 : sur un pilote qui la prend en charge (c'est le cas de
Longhorn), le système de fichiers est étendu **sans redémarrer le pod**. Les
événements du namespace le confirment :

```bash
kubectl -n <ns> get events --sort-by='.metadata.creationTimestamp' | tail -10
# Normal  FileSystemResizeSuccessful  persistentvolumeclaim/data-statefulset-elasticsearch-0
#   MountVolume.NodeExpandVolume succeeded for volume "pvc-3bdbaff0-..."
# Normal  FileSystemResizeSuccessful  pod/statefulset-elasticsearch-0
#   MountVolume.NodeExpandVolume succeeded for volume "pvc-3bdbaff0-..."
```

Si le pilote ne sait pas le faire à chaud, `df` affiche encore l'ancienne
taille : il faut alors redémarrer le pod
(`kubectl delete pod statefulset-elasticsearch-0`).

```bash
kubectl -n <ns> exec statefulset-elasticsearch-0 -- df -h /usr/share/elasticsearch/data
# /dev/...    4.0G  1.9G  2.1G   48% /usr/share/elasticsearch/data
```

L'initContainer ne recommence pas la restauration : il vérifie la présence du
fichier avant d'écrire.

### Remettre le chart en cohérence

Le cluster est réparé, mais le chart déclare toujours `2Gi`. Tant que ce n'est
pas corrigé, la prochaine livraison tentera de revenir en arrière.

`storage.elasticsearch.size: 4Gi` dans `values.yaml`, puis `helm upgrade` :

```
Forbidden: updates to statefulset spec for fields other than 'replicas',
'ordinals', 'template', 'persistentVolumeClaimRetentionPolicy' and
'minReadySeconds' are forbidden
```

`volumeClaimTemplates` est **immuable** : on ne peut pas modifier le
StatefulSet en place. Il faut supprimer l'objet sans toucher à ses pods, puis
laisser Helm le recréer :

```bash
kubectl -n <ns> delete statefulset statefulset-elasticsearch --cascade=orphan
helm upgrade --install monchart . -n <ns>
```

`--cascade=orphan` supprime l'objet mais laisse vivre le pod et son PVC : le
service n'est pas interrompu, et le nouveau StatefulSet adopte le pod existant.

### Vérifier

Le blocage `read_only_allow_delete` est alors levé **automatiquement** dès
qu'Elasticsearch repasse au-dessus du seuil `high` (vérification toutes les
30 s). Pour vérifier sans attendre le cron :

```bash
kubectl -n <ns> create job --from=cronjob/cronjob-report verif-1
kubectl -n <ns> logs job/verif-1
```

Si le blocage persiste, on peut le lever à la main :

```bash
kubectl -n <ns> exec statefulset-elasticsearch-0 -- \
  curl -s -XPUT 'http://localhost:9200/_all/_settings' \
  -H 'Content-Type: application/json' \
  -d '{"index.blocks.read_only_allow_delete": null}'
```

Dans les événements, la reprise est nette : le job lancé pendant l'opération
échoue encore, le suivant passe.

```
# Warning  BackoffLimitExceeded  job/cronjob-report-29833818  Job has reached the specified backoff limit
# Normal   Completed             job/cronjob-report-29833819  Job completed
```

## Après l'exercice

Cet exercice laisse le volume d'Elasticsearch à 4 Gi, alors que les autres
dossiers déclarent 2 Gi dans leur `values.yaml`. Comme `volumeClaimTemplates`
est immuable, un `helm upgrade` depuis un autre dossier serait rejeté. C'est
pour cela que l'exercice 13 se fait **en dernier**.

Pour revenir en arrière malgré tout : refaire la séquence
`kubectl delete statefulset statefulset-elasticsearch --cascade=orphan` puis
`helm upgrade` depuis le dossier voulu (le PVC, lui, restera à 4 Gi : on ne
rétrécit pas un volume).

## Rappel théorique

* Trois seuils de disque : `low` (plus d'allocation de nouveaux shards),
  `high` (déplacement des shards vers d'autres nœuds), `flood_stage` (index en
  **lecture seule**). Exprimables en pourcentage ou en valeur absolue d'espace
  libre restant.
* Depuis la 7.4, le blocage `flood_stage` est levé automatiquement dès le
  retour sous le seuil `high`. Avant, il fallait le lever à la main, et
  beaucoup de gens l'ignorent encore.
* Un cluster `green` ne garantit pas qu'on peut écrire.
* **Agrandir un volume se fait toujours en deux étapes** : le volume côté
  stockage, puis le système de fichiers dans le pod. Depuis Kubernetes 1.24,
  l'extension d'un volume **en cours d'utilisation** est stable : les deux
  étapes se font à chaud, sans redémarrer le pod, et l'événement
  `FileSystemResizeSuccessful` le confirme. Les pilotes qui ne le prennent pas
  en charge exigent un redémarrage du pod.
* Sur un StatefulSet, `volumeClaimTemplates` est immuable : la séquence est
  toujours « agrandir le ou les PVC à la main, puis `delete sts
  --cascade=orphan` et recréer ». Sur un StatefulSet à plusieurs replicas, il
  faut patcher **chaque** PVC.
* Corollaire : mieux vaut dimensionner généreusement dès le départ, ou surveiller
  le remplissage avant d'arriver au seuil.

---

*Retour à l'état sain : `diff -ru ../../00-initial ../../13` montre exactement
ce qui a été modifié.*
