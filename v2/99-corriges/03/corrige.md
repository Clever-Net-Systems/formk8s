# Corrigé - exercice 3 : Un pod qui redémarre sans raison apparente

| | |
|---|---|
| **Panne** | `livenessProbe` du backend pointée sur `/health` (404) au lieu de `/healthz` |
| **Fichier(s) modifié(s)** | `templates/deployment-backend.yml` |
| **Symptôme attendu** | pods backend `Running` mais redémarrés toutes les ~90 s |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

`templates/deployment-backend.yml`, sonde de vie :

```diff
           livenessProbe:
             httpGet:
-              path: /healthz
+              path: /health
```

`/health` n'existe pas dans la configuration nginx du backend : la sonde reçoit
un 404, donc un échec.

## Démarche de diagnostic

```bash
kubectl -n <ns> get pods -l tier=backend
# READY   STATUS    RESTARTS
# 1/1     Running   3 (45s ago)

kubectl -n <ns> describe pod -l tier=backend | grep -A3 -i liveness
#   Liveness:  http-get http://:http/health delay=0s timeout=3s period=30s #failure=3
#   Warning  Unhealthy  ... Liveness probe failed: HTTP probe failed with statuscode: 404
#   Normal   Killing    ... Container backend-container failed liveness probe, will be restarted
```

La sonde échoue 3 fois de suite (3 x 30 s), puis kubelet tue le conteneur. Le
pod reste `Ready` entre deux tueries parce que la sonde *readiness*, elle, vise
`/reports/` et fonctionne.

## Correction

Rétablir `path: /healthz` dans la `livenessProbe`, puis `helm upgrade`.

## Rappel théorique

* **liveness** : "faut-il redémarrer le conteneur ?" Un échec = redémarrage.
* **readiness** : "peut-on lui envoyer du trafic ?" Un échec = retrait des
  Endpoints du Service, sans redémarrage.
* **startup** : "a-t-il fini de démarrer ?" Tant qu'elle n'est pas passée,
  liveness et readiness sont suspendues. Indispensable pour les applications
  lentes (Elasticsearch ici).
* Une liveness trop stricte (ou qui vise une dépendance externe) est une cause
  classique de redémarrages en cascade en production.

---

*Retour à l'état sain : `diff -ru ../../00-initial ../../03` montre exactement
ce qui a été modifié.*
