# Exercice 13 - Elasticsearch passe en lecture seule

| | |
|---|---|
| **Difficulte** | ***** |
| **Duree indicative** | 25 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
# Cet exercice change la taille d'un volume : un PVC ne peut pas retrecir,
# il faut donc repartir d'une installation neuve.
helm uninstall monchart -n <prenom>-tshoot
kubectl -n <prenom>-tshoot delete pvc --all

cd v2/13
helm install monchart . -n <prenom>-tshoot
```

## Contexte

Nouvelle installation de la plateforme sur un environnement ou le stockage a
ete dimensionne au plus juste. Tout demarre correctement : les pods sont verts,
le cluster Elasticsearch est `green`... mais le CronJob echoue a chaque
execution.

## Ce que vous devez constater

* `statefulset-elasticsearch-0` est `Running 1/1`
* `curl http://service-elasticsearch:9200/_cluster/health` renvoie `green`
* les Jobs `cronjob-report` echouent tous, et le rapport n'est plus mis a jour

## Votre mission

Comprendre pourquoi Elasticsearch refuse d'ecrire alors qu'il se declare en
bonne sante, et retablir le service durablement.

Attention : cet exercice demande de modifier le volume d'un **StatefulSet**.
Lisez le message d'erreur de `helm upgrade` avant de vous lancer.

## Questions pour vous guider

* Que disent les logs d'un Job en echec ? Cherchez le mot `block`.
* Un cluster `green` signifie que les shards sont alloues. Cela garantit-il que
  l'on peut y ecrire ?
* `kubectl exec statefulset-elasticsearch-0 -- df -h /usr/share/elasticsearch/data`
* Quels seuils sont configures dans `configmap-elasticsearch` ? Comparez-les a
  l'espace libre reel.
* Quelle est la taille du volume, et d'ou vient-elle ?
  `kubectl get pvc data-statefulset-elasticsearch-0`
* Essayez de changer `storage.elasticsearch.size` dans `values.yaml` puis de
  faire `helm upgrade` : que repond l'API, et pourquoi ?

## Critere de reussite

Un nouveau `report-*.txt` est ecrit, les Jobs repassent en `Complete`, le PVC
d'Elasticsearch fait la nouvelle taille, et `helm upgrade` fonctionne a nouveau
sans erreur.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'apres avoir trouve, ou si vous etes vraiment bloque.*
