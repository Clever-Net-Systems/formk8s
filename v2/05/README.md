# Exercice 5 - Elasticsearch ne demarre plus apres un ajustement de memoire

| | |
|---|---|
| **Difficulte** | ***.. |
| **Duree indicative** | 15 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/05
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Pour "faire de la place sur le cluster", la limite memoire d'Elasticsearch a
ete revue a la baisse. Depuis, le pod ne demarre plus.

## Ce que vous devez constater

* `statefulset-elasticsearch-0` redemarre en boucle
* ses logs sont vides, ou s'arretent en plein milieu du demarrage de la JVM
* les jobs `cronjob-report` commencent a echouer

## Votre mission

Trouver qui tue le conteneur et pourquoi, puis corriger.

## Questions pour vous guider

* Les logs ne disent rien : ou trouver la raison de l'arret du conteneur
  precedent ? (cherchez `Last State` et `Exit Code`)
* Que signifie un code de sortie 137 ?
* Quel rapport entre la taille du tas de la JVM (`ES_JAVA_OPTS`) et la limite
  memoire du conteneur ? Quelle marge faut-il garder, et pour quoi faire ?
* Deux corrections sont possibles : laquelle est la bonne ici, et pourquoi ?

## Critere de reussite

`statefulset-elasticsearch-0` est `Running 1/1` de maniere stable, et
`helm test monchart` repasse au vert.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'apres avoir trouve, ou si vous etes vraiment bloque.*
