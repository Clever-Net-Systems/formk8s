# TP de troubleshooting Kubernetes

Une application 3 tiers volontairement saine (`00-initial`), puis 13 copies de
cette application dans lesquelles une panne a ete introduite. Les etudiants
installent une copie, constatent le symptome, diagnostiquent avec `kubectl`,
puis corrigent le chart eux-memes.

| Dossier | Contenu |
|---|---|
| `00-initial/` | le chart Helm de reference, **il fonctionne parfaitement** |
| `01/` a `13/` | une copie du chart avec **une** panne, plus `README.md` (enonce) et `corrige.md` (solution) |
| `namespace-restricted.yaml` | le namespace de TP, avec Pod Security Admission `enforce: restricted` |
| `architecture.svg` / `.png` | le schema ci-dessous |

Chaque dossier repart de `00-initial` : **les pannes ne sont pas cumulatives**.
`diff -ru 00-initial 07` montre exactement ce qui a ete casse.

---

## Ce que deploie le chart

![Architecture de l'application](architecture.png)

Une application **3 tiers** plus un traitement par lot. Le point important pour
la formation : **chaque maillon casse se voit depuis le navigateur**, et le
diagnostic se fait ensuite avec `kubectl`.

### Les quatre composants

**`deployment-frontend`** (nginx non-root, 2 replicas)
Sert une page HTML qui affiche en direct l'etat de la chaine : backend
joignable ou non, fraicheur du dernier rapport, etat du cluster Elasticsearch.
La page se rafraichit toutes les 15 s et indique quel pod a repondu.
Il proxifie `/api/` vers le tier backend ; si celui-ci ne repond pas, il renvoie
une 503 explicite plutot qu'une erreur brute.

**`deployment-backend`** (nginx non-root, 2 replicas)
Il n'est **pas expose a l'exterieur** : seul le frontend l'appelle, par le nom
DNS de son Service ClusterIP. Pour le tester directement depuis un poste de
travail : `kubectl port-forward svc/service-backend-clusterip 8080:80`.
Monte le volume partage **en lecture seule** et le publie sous `/reports/`.
Expose aussi `/healthz` et `/whoami`. Sa sonde *readiness* tape sur `/reports/`,
donc un probleme de volume se traduit par un pod `Running` mais `0/1 Ready`.

**`cronjob-report`** (image curl, toutes les minutes)
1. verifie qu'il peut ecrire a la racine du volume partage ;
2. interroge Elasticsearch (30 s d'attente maximum ; une indisponibilite n'est
   pas fatale, le rapport est quand meme ecrit) ;
3. cree l'index `formation-reports` s'il n'existe pas ;
4. ecrit `report-<horodatage>.txt` et `latest.txt` sur le volume partage ;
5. indexe un document dans Elasticsearch ;
6. ne conserve que les 20 derniers rapports.

Un rapport ressemble a ceci :

```
date          : 2026-09-21T13:08:23Z
job           : cronjob-report-29012345-abcde
attente ES    : 0s
elasticsearch : http://service-elasticsearch.<ns>.svc.cluster.local:9200
index         : formation-reports
cluster health: {"cluster_name":"formation-troubleshooting","status":"green",...}
documents     : {"count":3,...}   (avant ce run)
```

**`statefulset-elasticsearch`** (1 pod)
Elasticsearch 8.15 mono-noeud, securite desactivee (pas de mot de passe ni de
TLS a gerer en formation), avec son propre volume `ReadWriteOnce` cree par
`volumeClaimTemplates` et un Service **headless**.

### Ce qu'on voit quand tout marche

* la page du frontend : trois pastilles vertes ;
* `/api/reports/` sur le frontend : un fichier de plus chaque minute ;
* `kubectl get jobs -l tier=report` : des Jobs `Complete` ;
* `helm test monchart` : les 7 verifications passent.

### Objets Kubernetes crees

| Type | Nom | Role |
|---|---|---|
| Deployment | `deployment-frontend`, `deployment-backend` | les deux tiers nginx |
| StatefulSet | `statefulset-elasticsearch` | Elasticsearch mono-noeud |
| CronJob | `cronjob-report` | le rapport, chaque minute |
| Service | `service-frontend-nodeport` | NodePort -> frontend |
| Service | `service-backend-clusterip` | ClusterIP -> backend, interne au cluster |
| Service | `service-elasticsearch` | headless (`clusterIP: None`) |
| PVC | `pvc-reports` | volume partage **ReadWriteMany** |
| PVC | `data-statefulset-elasticsearch-0` | donnees Elasticsearch (cree par le StatefulSet) |
| ConfigMap | `configmap-myapp` | configuration applicative (APPID) |
| ConfigMap | `configmap-frontend`, `configmap-backend` | configurations nginx et pages HTML |
| ConfigMap | `configmap-elasticsearch` | parametres Elasticsearch |
| ConfigMap | `configmap-report-script` | le script du CronJob |
| Secret | `secret-myapp` | mot de passe applicatif |
| Pod | `pod-test-connection` | cree et supprime par `helm test` |

Trois images publiques, aucune image custom :
`nginxinc/nginx-unprivileged:1.27-alpine`, `curlimages/curl:8.11.1`,
`docker.elastic.co/elasticsearch/elasticsearch:8.15.3`.

---

## Les exercices

| # | Titre | Difficulte | Duree | Notion travaillee |
|---|---|---|---|---|
| [01](01/) | Le deploiement ne se termine jamais | `*....` | 10 min | `ImagePullBackOff`, evenements du pod |
| [02](02/) | Le tier backend redemarre en boucle | `**...` | 15 min | `CrashLoopBackOff`, `logs --previous` |
| [03](03/) | Un pod qui redemarre sans raison apparente | `**...` | 15 min | sondes liveness / readiness / startup |
| [04](04/) | Des pods qui restent en Pending | `*....` | 10 min | scheduling, `requests` et `limits` |
| [05](05/) | Elasticsearch ne demarre plus apres un ajustement | `***..` | 15 min | `OOMKilled`, memoire d'une JVM en conteneur |
| [06](06/) | Le backend est en bonne sante mais injoignable | `***..` | 15 min | Service ClusterIP, selecteurs, Endpoints |
| [07](07/) | Une 503 qui n'apparait que dans les logs | `***..` | 15 min | logs applicatifs, `port` et `targetPort` |
| [08](08/) | La configuration a change, l'application non | `***..` | 15 min | ConfigMap, `envFrom`, `rollout restart` |
| [09](09/) | Plus aucun rapport depuis ce matin | `***..` | 20 min | CronJob, Jobs, historique et logs |
| [10](10/) | Un Job qui ne cree aucun pod | `****.` | 15 min | Pod Security Admission, refus a l'admission |
| [11](11/) | Des pods evinces les uns apres les autres | `****.` | 15 min | stockage ephemere, eviction |
| [12](12/) | Volume partage sature | `****.` | 20 min | volume RWX plein, extension d'un PVC |
| [13](13/) | Elasticsearch passe en lecture seule | `*****` | 25 min | seuils de disque ES, resize d'un StatefulSet |

### Deroule propose pour 4 h

Les 13 exercices representent **3 h 25 de manipulation seule** : ils ne tiennent
pas en 4 h avec les rappels theoriques. Parcours conseille, **10 exercices** :

| Temps | Contenu |
|---|---|
| 0:00 - 0:20 | Methode de diagnostic : `get` / `describe` / `logs` / `events`, ou chercher selon le symptome |
| 0:20 - 1:00 | Exercices **01, 02, 03** - cycle de vie d'un pod et sondes |
| 1:00 - 1:15 | Rappel : `requests` / `limits`, QoS, eviction |
| 1:15 - 1:45 | Exercices **04, 05** |
| 1:45 - 2:00 | Pause |
| 2:00 - 2:15 | Rappel : Service, Endpoints, DNS interne |
| 2:15 - 2:45 | Exercices **06, 07** |
| 2:45 - 3:05 | Exercice **09** (CronJob) |
| 3:05 - 3:20 | Rappel : Pod Security Admission et profil `restricted` |
| 3:20 - 3:35 | Exercice **10** |
| 3:35 - 4:00 | Exercice **13** (le plus riche : stockage, StatefulSet, seuils ES) |

Les exercices **08, 11 et 12** restent disponibles en bonus, ou pour remplacer
un exercice du parcours selon le public. Si la session est plus courte, les
exercices 01 a 06 forment un socle coherent.

### Comment se deroule un exercice

```bash
cd v2/01
helm upgrade --install monchart . -n <prenom>-tshoot

# observer, diagnostiquer, corriger les fichiers du dossier 01, puis :
helm upgrade --install monchart . -n <prenom>-tshoot
```

Le `README.md` du dossier donne le contexte, ce qu'il faut constater et des
questions pour guider la recherche. Le `corrige.md` donne la panne exacte, la
demarche de diagnostic pas a pas, la correction et un rappel theorique :
**il n'est pas distribue avant la fin de l'exercice**.

Les exercices **12 et 13** modifient la taille d'un volume : ils demandent une
installation neuve (un PVC ne peut pas retrecir), et il faut egalement
desinstaller proprement avant de passer a la suite :

```bash
helm uninstall monchart -n <prenom>-tshoot
kubectl -n <prenom>-tshoot delete pvc --all
```

---

## Prerequis

* Kubernetes >= 1.25, Helm 3 ou 4.
* ~1,5 Gio de RAM pour Elasticsearch.
* Une **StorageClass ReadWriteMany** (`longhorn` par defaut, cf.
  `00-initial/values.yaml`). Le CronJob ecrit a la racine de ce volume en
  **non-root** : cette racine doit donc etre inscriptible. A verifier une fois :

  ```bash
  kubectl get csidriver -o custom-columns=NAME:.metadata.name,FSGROUP:.spec.fsGroupPolicy
  ```

  `fsGroupPolicy=File` : bon. `ReadWriteOnceWithFSType` (le defaut) : `fsGroup`
  est ignore sur un PVC RWX, il faut alors que le provisionneur cree la racine
  deja inscriptible (beaucoup d'exports NFS la creent en 0777). Sinon, le
  CronJob s'arrete avec un diagnostic explicite dans ses logs.
* Pour les exercices 12 et 13 : une StorageClass avec
  `allowVolumeExpansion: true`.

## Installation

```bash
# le namespace, en mode restricted (une seule fois)
sed 's/<prenom>/antoine/' namespace-restricted.yaml | kubectl apply -f -

cd 00-initial
helm upgrade --install monchart . -n antoine-tshoot
```

Tout est dans `00-initial/values.yaml`, il n'y a pas d'autre fichier de valeurs
et rien a surcharger. Sur un cluster mono-noeud sans RWX reel (kind, minikube) :
ajouter `--set storage.reports.storageClassName= --set storage.elasticsearch.storageClassName=`.

## Verification

```bash
kubectl -n antoine-tshoot rollout status deploy/deployment-backend --timeout=3m
kubectl -n antoine-tshoot rollout status statefulset/statefulset-elasticsearch --timeout=5m
kubectl -n antoine-tshoot rollout status deploy/deployment-frontend --timeout=3m

helm test monchart -n antoine-tshoot --logs

export NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
export FRONTEND_PORT=$(kubectl -n antoine-tshoot get svc service-frontend-nodeport -o jsonpath='{.spec.ports[0].nodePort}')
echo "frontend : http://$NODE_IP:$FRONTEND_PORT/"
echo "rapports : http://$NODE_IP:$FRONTEND_PORT/api/reports/"

# le backend n'est pas expose sur les noeuds : tunnel depuis le poste de travail
kubectl -n antoine-tshoot port-forward svc/service-backend-clusterip 8080:80
#   -> http://localhost:8080/reports/
```

Le premier rapport apparait au bout d'une minute. Pour ne pas attendre :

```bash
kubectl -n antoine-tshoot create job --from=cronjob/cronjob-report report-manuel-1
kubectl -n antoine-tshoot logs job/report-manuel-1
```

## Desinstallation

```bash
helm uninstall monchart -n antoine-tshoot
# le PVC du StatefulSet n'est PAS supprime par Helm :
kubectl -n antoine-tshoot delete pvc data-statefulset-elasticsearch-0
```

---

## Pourquoi ces choix (namespace `restricted`)

Le namespace interdit root, les capabilities, l'escalade de privileges, et
impose `seccompProfile`. D'ou :

* **`nginxinc/nginx-unprivileged`** et non `nginx` : l'image standard demarre en
  root et ecoute sur le port 80 (< 1024). Ici : UID 101, port 8080.
* **Aucun initContainer privilegie** pour Elasticsearch : le `chown -R` habituel
  est remplace par `fsGroup: 1000`, et le `sysctl vm.max_map_count` par
  `node.store.allow_mmap: false`. `discovery.type: single-node` desactive en
  prime les *bootstrap checks*.
* **Meme `fsGroup: 2000`** sur le backend et sur le CronJob, pour le volume
  partage : c'est l'ecrivain (le CronJob) qui en a reellement besoin.

## Pieges connus (utiles en TP)

* **Un pod refuse par Pod Security n'apparait pas dans `kubectl get pods`.** Le
  Deployment est accepte, `helm upgrade` affiche `deployed`, et c'est le
  ReplicaSet (ou le Job) qui echoue : `kubectl describe rs -l tier=frontend`.
* **`Running` mais `0/1 Ready` sur le backend** = probleme de volume (404 si le
  montage est absent, 403 s'il est illisible). Un volume qui ne se monte pas du
  tout laisse le pod **avant** `Running` (`ContainerCreating` + `FailedMount`).
* **Un PVC peut grandir, jamais retrecir**, et la taille d'un
  `volumeClaimTemplates` de StatefulSet est immuable.
* **`appName` finit dans `spec.selector`**, immuable : le changer sur une
  release installee fait echouer `helm upgrade`.
* **`envFrom` ignore silencieusement** les cles de ConfigMap qui ne sont pas des
  noms de variables valides (evenement `InvalidEnvironmentVariableNames`).
* **Un seul release par namespace** : les noms des ressources sont fixes.
