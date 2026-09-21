# Exercice 13 - Elasticsearch passe en lecture seule

| | |
|---|---|
| **Difficulté** | ***** |
| **Durée indicative** | 25 min |
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

Nouvelle installation de la plateforme sur un environnement où le stockage a
été dimensionné au plus juste. Tout démarre correctement, les pods sont tous
`Running`, Elasticsearch répond... mais le CronJob échoue à chaque exécution.

## Ce que vous devez constater

* `statefulset-elasticsearch-0` est `Running 1/1` et répond sur le port 9200
* les Jobs `cronjob-report` échouent tous
* le rapport, lui, continue d'être écrit chaque minute sur le volume partagé :
  ce n'est donc ni le volume, ni le backend

## Votre mission

Comprendre pourquoi Elasticsearch refuse d'écrire alors qu'il se déclare en
bonne santé, et rétablir le service durablement.

Attention : cet exercice demande de modifier le volume d'un **StatefulSet**.
Lisez le message d'erreur de `helm upgrade` avant de vous lancer.

## Questions pour vous guider

* Que disent les logs d'un Job en échec ? Cherchez le mot `block`.
* Elasticsearch se déclare en bonne santé et répond aux lectures. Est-ce que
  cela garantit que l'on peut y écrire ?
* `kubectl exec statefulset-elasticsearch-0 -- df -h /usr/share/elasticsearch/data`
* Quels seuils sont configurés dans `configmap-elasticsearch` ?
  Comparez-les à l'espace libre réel.
* Quelle est la taille du volume, et d'où vient-elle ?
  `kubectl get pvc data-statefulset-elasticsearch-0`
* Essayez de changer `storage.elasticsearch.size` dans `values.yaml` puis de
  faire `helm upgrade` : que répond l'API, et pourquoi ?

## Critère de réussite

Les Jobs `cronjob-report` repassent en `Complete`, le PVC d'Elasticsearch fait
la nouvelle taille, et `helm upgrade` fonctionne à nouveau sans erreur.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'après avoir trouvé, ou si vous êtes vraiment bloqué.*
