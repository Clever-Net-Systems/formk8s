# Exercice 3 - Un pod qui redemarre sans raison apparente

| | |
|---|---|
| **Difficulte** | **... |
| **Duree indicative** | 15 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/03
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Les utilisateurs signalent des coupures breves et regulieres sur l'API. Les
pods backend semblent pourtant fonctionner : ils repondent quand on les teste.

## Ce que vous devez constater

* les pods backend sont `Running` et `Ready`, mais leur compteur `RESTARTS`
  augmente toutes les une a deux minutes
* entre deux redemarrages, l'application repond parfaitement

## Votre mission

Comprendre qui tue le conteneur, et corriger le chart.

Patientez au moins deux minutes apres le `helm upgrade` avant de conclure.

## Questions pour vous guider

* Qui peut decider de redemarrer un conteneur qui ne plante pas tout seul ?
* Que racontent les evenements du pod ?
* Testez a la main l'URL interrogee par la sonde :
  `kubectl exec deploy/deployment-backend -- curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/<chemin>`
* Quelle est la difference de consequence entre une sonde *liveness* qui echoue
  et une sonde *readiness* qui echoue ?

## Critere de reussite

`RESTARTS` reste a 0 pendant plusieurs minutes.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'apres avoir trouve, ou si vous etes vraiment bloque.*
