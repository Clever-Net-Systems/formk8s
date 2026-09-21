# Exercice 5 - Elasticsearch ne démarre plus après un ajustement de mémoire

| | |
|---|---|
| **Difficulté** | ***.. |
| **Durée indicative** | 15 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/05
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Pour "faire de la place sur le cluster", la limite mémoire d'Elasticsearch a
été revue à la baisse. Depuis, le pod ne démarre plus.

## Ce que vous devez constater

* `statefulset-elasticsearch-0` redémarre en boucle
* ses logs sont vides, ou s'arrêtent en plein milieu du démarrage de la JVM
* les jobs `cronjob-report` commencent à échouer

## Votre mission

Trouver qui tue le conteneur et pourquoi, puis corriger.

## Questions pour vous guider

* Les logs ne disent rien : où trouver la raison de l'arrêt du conteneur
  précédent ? (cherchez `Last State` et `Exit Code`)
* Que signifie un code de sortie 137 ?
* Quel rapport entre la taille du tas de la JVM (`ES_JAVA_OPTS`) et la limite
  mémoire du conteneur ? Quelle marge faut-il garder, et pour quoi faire ?
* Deux corrections sont possibles : laquelle est la bonne ici, et pourquoi ?

## Critère de réussite

`statefulset-elasticsearch-0` est `Running 1/1` de manière stable, et
`helm test monchart` repasse au vert.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'après avoir trouvé, ou si vous êtes vraiment bloqué.*
