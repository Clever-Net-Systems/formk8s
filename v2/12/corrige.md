# Corrigé - exercice 12 : Volume partagé saturé

| | |
|---|---|
| **Panne** | volume partagé réduit à `64Mi` et Job d'import qui le remplit jusqu'à saturation |
| **Fichier(s) modifié(s)** | `values.yaml`, `templates/job-import-dump.yml` (ajouté) |
| **Symptôme attendu** | CronJob en échec : impossible d'écrire, volume à 100 % |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

1. `values.yaml` : le volume partagé passe de `1Gi` à `64Mi`.
2. Ajout de `templates/job-import-dump.yml`, qui écrit jusqu'à saturation
   (`dd if=/dev/zero of=/data/dump-import.bin bs=1M`, sans `count`).

Le volume est donc plein à 100 %, et le CronJob ne peut plus rien écrire.

## Démarche de diagnostic

```bash
kubectl -n <ns> logs -l tier=report --tail=-1 | tail -15
# ERREUR : impossible d'ecrire dans /data.
#          UID/GID du conteneur : 65534:65534, groupes : 65534 2000
#          Droits du point de montage :
# drwxrwsr-x 2 nobody 2000 ...
#          Espace disponible :
# Filesystem  Size  Used Avail Use% Mounted on
# ...          60M   60M     0 100% /data
#          Pistes : volume plein (voir ci-dessus), ou bien : ...
```

Les droits sont bons (`drwxrwsr-x`, groupe 2000) : c'est bien l'espace qui
manque. Confirmation côté backend :

```bash
kubectl -n <ns> exec deploy/deployment-backend -- df -h /data
kubectl -n <ns> exec deploy/deployment-backend -- ls -lh /data
# -rw-r--r-- 1 nobody 2000 58.2M dump-import.bin
```

## Correction

**Immédiate** (libérer de la place). Le backend monte le volume en lecture
seule : il faut écrire depuis un pod qui l'a en écriture, par exemple un job de
rapport déclenché à la main, ou un pod jetable conforme au profil restricted :

```bash
kubectl -n <ns> delete job job-import-dump
kubectl -n <ns> run purge --rm -it --restart=Never --image=curlimages/curl:8.11.1 \
  --overrides='{"spec":{"securityContext":{"runAsNonRoot":true,"runAsUser":65534,"fsGroup":2000,"seccompProfile":{"type":"RuntimeDefault"}},"containers":[{"name":"purge","image":"curlimages/curl:8.11.1","command":["sh","-c","rm -f /data/dump-import.bin; df -h /data"],"securityContext":{"allowPrivilegeEscalation":false,"capabilities":{"drop":["ALL"]}},"volumeMounts":[{"name":"r","mountPath":"/data"}]}],"volumes":[{"name":"r","persistentVolumeClaim":{"claimName":"pvc-reports"}}]}}'
```

**Durable** (agrandir le volume) :

```bash
kubectl -n <ns> get sc <classe> -o jsonpath='{.allowVolumeExpansion}{"\n"}'   # doit valoir true
kubectl -n <ns> patch pvc pvc-reports -p '{"spec":{"resources":{"requests":{"storage":"1Gi"}}}}'
kubectl -n <ns> get pvc pvc-reports -w
```

Puis remettre `size: 1Gi` dans `values.yaml` pour que le chart reste la source
de vérité (sans cela, le prochain `helm upgrade` tentera de revenir à 64Mi et
sera rejeté).

Selon le pilote CSI, l'extension d'un volume ReadWriteMany peut exiger que plus
aucun pod ne l'utilise : dans ce cas, `kubectl scale deploy/deployment-backend
--replicas=0`, suspendre le CronJob (`kubectl patch cronjob cronjob-report -p
'{"spec":{"suspend":true}}'`), agrandir, puis tout remonter.

Enfin, supprimer le Job d'import du chart (ou le rendre borné, par exemple
`count=10`) : c'est lui la cause réelle.

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

*Retour à l'état sain : `diff -ru ../00-initial ../12` montre exactement
ce qui a été modifié.*
