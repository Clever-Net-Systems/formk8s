# Exercice 13 - Elasticsearch passe en lecture seule

| | |
|---|---|
| **Difficulté** | ***** |
| **Durée indicative** | 25 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/13
helm upgrade --install monchart . -n <prenom>-tshoot
```

Le pod Elasticsearch est recréé et commence par restaurer un jeu de données :
comptez une à deux minutes avant qu'il ne repasse `Running`.

Ce dossier déclare `storage.reports.size: 2Gi`, car il prend la suite de
l'exercice 12 où le volume partagé a été agrandi. Un chart qui déclarerait
encore `1Gi` serait refusé par l'API : on ne rétrécit pas un PVC.

## Contexte

L'équipe data a livré une restauration de snapshot : un initContainer dépose
son jeu de données sur le volume d'Elasticsearch avant que celui-ci ne démarre.

Depuis, tous les Jobs du CronJob échouent — alors qu'Elasticsearch démarre
normalement et répond quand on l'interroge.

## Ce que vous devez constater

* `statefulset-elasticsearch-0` est `Running 1/1` et répond sur le port 9200
* les Jobs `cronjob-report` échouent tous
* le rapport, lui, continue d'être écrit chaque minute sur le volume partagé :
  ce n'est donc ni le volume partagé, ni le tier backend

## Votre mission

Comprendre pourquoi Elasticsearch refuse d'écrire alors qu'il répond, et
rétablir le service **sans perdre les données restaurées**.

## Questions pour vous guider

* Que disent les logs d'un Job en échec ? Quel code HTTP est renvoyé ?
* Elasticsearch répond aux lectures. Est-ce que cela garantit que l'on peut y
  écrire ? Cherchez le mot `flood` dans ses logs.
* Dans quel état est réellement son disque ?
  `kubectl exec statefulset-elasticsearch-0 -- df -h /usr/share/elasticsearch/data`
* Et que contient ce volume ?
  `kubectl exec statefulset-elasticsearch-0 -- ls -lh /usr/share/elasticsearch/data`
* Les données restaurées doivent être conservées : il ne reste donc qu'une
  seule solution. Laquelle ?
* Changez `storage.elasticsearch.size` dans `values.yaml`, lancez
  `helm upgrade` : que répond l'API, et pourquoi ?
* Une fois le PVC agrandi, le système de fichiers du pod voit-il tout de suite
  la nouvelle taille ?

## Critère de réussite

`df` montre de l'espace libre, le fichier restauré est toujours là, les Jobs
`cronjob-report` repassent en `Complete`, et `helm upgrade` fonctionne à
nouveau sans erreur.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'après avoir trouvé, ou si vous êtes vraiment bloqué.*
