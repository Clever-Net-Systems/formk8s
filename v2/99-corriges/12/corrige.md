# Corrigé - exercice 12 : Volume partagé saturé

| | |
|---|---|
| **Panne** | Job d'import ajouté, qui remplit le volume partagé jusqu'à saturation |
| **Fichier(s) modifié(s)** | `templates/job-import-dump.yml` (ajouté) |
| **Symptôme attendu** | CronJob en échec : impossible d'écrire, volume à 100 % |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

Ajout de `templates/job-import-dump.yml`, qui écrit sur le volume partagé sans
aucune limite :

```yaml
              dd if=/dev/zero of="$REPORT_DIR/dump-import.bin" bs=1M 2>/dev/null || true
```

Pas de `count` : `dd` ne s'arrête que lorsqu'il n'y a plus de place. Le volume
est donc plein à 100 %, et le CronJob ne peut plus rien écrire.

## Démarche de diagnostic

```bash
kubectl -n <ns> logs -l tier=report --tail=-1 | tail -15
# ERREUR : impossible d'ecrire dans /data.
#          UID/GID du conteneur : 65534:65534, groupes : 65534 2000
#          Droits du point de montage :
# drwxrwsr-x 2 nobody 2000 ...
#          Espace disponible :
# Filesystem  Size  Used Avail Use% Mounted on
# ...          976M  976M     0 100% /data
#          Pistes : volume plein (voir ci-dessus), ou bien : ...
```

Selon l'endroit exact où l'écriture échoue, le script affiche soit ce message
(le pré-vol), soit `ERREUR : écriture de /data/report-....txt impossible` : dans
les deux cas il termine par la sortie de `df`, et c'est elle qui tranche.

Les droits sont bons (`drwxrwsr-x`, groupe 2000) : c'est bien l'espace qui
manque. Confirmation côté backend :

```bash
kubectl -n <ns> exec deploy/deployment-backend -- df -h /data
kubectl -n <ns> exec deploy/deployment-backend -- ls -lh /data
# -rw-r--r-- 1 nobody 2000 944.6M dump-import.bin
```

## Correction

Deux choses à faire.

**1. Agrandir le volume.** C'est ce que demande la situation : 1 Gi ne suffit
plus. Ce PVC est géré par Helm, on le corrige donc **dans le chart**, pas dans
le cluster. La StorageClass doit autoriser l'extension :

```bash
kubectl get sc <classe> -o jsonpath='{.allowVolumeExpansion}{"\n"}'   # doit valoir true
```

puis `storage.reports.size: 2Gi` dans `values.yaml`, et `helm upgrade` : Helm
agrandit le PVC et garde la propriété du champ.

```bash
kubectl -n <ns> get pvc pvc-reports
# NAME          STATUS   CAPACITY   ACCESS MODES
# pvc-reports   Bound    2Gi        RWX
```

Il reste alors environ 1 Gi libre : le CronJob repart tout seul à la minute
suivante.

> **Ne pas agrandir ce PVC avec `kubectl patch` ou `kubectl edit`.** Helm 4
> applique les objets **côté serveur** : le champ modifié changerait de
> propriétaire, et les `helm upgrade` suivants échoueraient avec
> `conflict with "kubectl-edit" using v1: .spec.resources.requests.storage`.
> Il faudrait alors repasser par `helm upgrade --force-conflicts`. La règle :
> **un objet géré par Helm se corrige dans le chart**.

**2. Traiter la cause.** Le Job d'import écrit sans aucune limite : tel quel,
il remplirait de nouveau n'importe quel volume, quelle que soit sa taille. Le
supprimer du chart (`templates/job-import-dump.yml`), ou le borner avec un
`count`.

### Variante : libérer la place au lieu d'agrandir

Le tier backend monte le volume en lecture seule ; il faut donc écrire depuis
un pod qui l'a en écriture, conforme au profil `restricted` :

```bash
kubectl -n <ns> delete job job-import-dump
kubectl -n <ns> run purge --rm -it --restart=Never --image=curlimages/curl:8.11.1 \
  --overrides='{"spec":{"securityContext":{"runAsNonRoot":true,"runAsUser":65534,"fsGroup":2000,"seccompProfile":{"type":"RuntimeDefault"}},"containers":[{"name":"purge","image":"curlimages/curl:8.11.1","command":["sh","-c","rm -f /data/dump-import.bin; df -h /data"],"securityContext":{"allowPrivilegeEscalation":false,"capabilities":{"drop":["ALL"]}},"volumeMounts":[{"name":"r","mountPath":"/data"}]}],"volumes":[{"name":"r","persistentVolumeClaim":{"claimName":"pvc-reports"}}]}}'
```

Cette voie suffit à relancer la production de rapports. Elle ne vaudrait rien
si le fichier déposé était une donnée légitime — c'est d'ailleurs exactement le
cas de figure de l'exercice 13.

Deux limites à garder en tête :

* on ne peut qu'**agrandir**. Une fois le volume passé à 2 Gi, un chart qui
  déclare encore `1Gi` sera rejeté (`field can not be less than
  status.capacity`) : c'est pour cette raison que le dossier de l'exercice 13
  déclare déjà `2Gi` ;
* selon le pilote CSI, l'extension d'un volume ReadWriteMany peut exiger que
  plus aucun pod ne l'utilise : dans ce cas `kubectl scale
  deploy/deployment-backend --replicas=0`, suspendre le CronJob
  (`kubectl patch cronjob cronjob-report -p '{"spec":{"suspend":true}}'`),
  agrandir, puis tout remonter.

## Rappel théorique

* Un PVC peut **grandir** (si `allowVolumeExpansion: true` sur la StorageClass)
  mais **jamais rétrécir** : `spec.resources.requests.storage` ne peut pas
  diminuer. C'est pour cela que cet exercice demande une installation neuve.
* Deux étapes dans une extension : le volume côté stockage, puis le système de
  fichiers dans le pod. Certaines classes font les deux à chaud, d'autres
  exigent un détachement.
* Un volume partagé sans quota ni rotation est une panne qui attend son heure :
  ici le CronJob fait sa propre rotation (`keepReports`), mais rien n'empêche un
  tiers d'y déposer un fichier énorme.

---

*Retour à l'état sain : `diff -ru ../../00-initial ../../12` montre exactement
ce qui a été modifié.*
