# Exercice 3 - Un pod qui redémarre sans raison apparente

| | |
|---|---|
| **Difficulté** | **... |
| **Durée indicative** | 15 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/03
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

L'exploitation a remarqué que les pods du tier backend redémarrent tout seuls,
plusieurs fois par heure. L'application, elle, répond correctement : le service
n'a jamais été interrompu.

## Ce que vous devez constater

* les pods backend sont `Running` et `Ready`, mais leur compteur `RESTARTS`
  augmente toutes les une à deux minutes
* entre deux redémarrages, l'application répond parfaitement

## Votre mission

Comprendre qui tue le conteneur, et corriger le chart.

Patientez au moins deux minutes après le `helm upgrade` avant de conclure.

## Questions pour vous guider

* Qui peut décider de redémarrer un conteneur qui ne plante pas tout seul ?
* Que racontent les événements du pod ?
* Testez à la main l'URL interrogée par la sonde :
  `kubectl exec deploy/deployment-backend -- curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/<chemin>`
* Quelle est la différence de conséquence entre une sonde *liveness* qui échoue
  et une sonde *readiness* qui échoue ?

## Critère de réussite

`RESTARTS` reste à 0 pendant plusieurs minutes.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'après avoir trouvé, ou si vous êtes vraiment bloqué.*
