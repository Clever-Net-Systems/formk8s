# Corrige - exercice 3 : Un pod qui redemarre sans raison apparente

| | |
|---|---|
| **Panne** | `livenessProbe` du backend pointee sur `/health` (404) au lieu de `/healthz` |
| **Fichier(s) modifie(s)** | `templates/deployment-backend.yml` |
| **Symptome attendu** | pods backend `Running` mais redemarres toutes les ~90 s |

> A ne pas distribuer aux etudiants avant la fin de l'exercice.

## La panne injectee

`templates/deployment-backend.yml`, sonde de vie :

```diff
           livenessProbe:
             httpGet:
-              path: /healthz
+              path: /health
```

`/health` n'existe pas dans la configuration nginx du backend : la sonde recoit
un 404, donc un echec.

## Demarche de diagnostic

```bash
kubectl -n <ns> get pods -l tier=backend
# READY   STATUS    RESTARTS
# 1/1     Running   3 (45s ago)

kubectl -n <ns> describe pod -l tier=backend | grep -A3 -i liveness
#   Liveness:  http-get http://:http/health delay=0s timeout=3s period=30s #failure=3
#   Warning  Unhealthy  ... Liveness probe failed: HTTP probe failed with statuscode: 404
#   Normal   Killing    ... Container backend-container failed liveness probe, will be restarted
```

La sonde echoue 3 fois de suite (3 x 30 s), puis kubelet tue le conteneur. Le
pod reste `Ready` entre deux tueries parce que la sonde *readiness*, elle, vise
`/reports/` et fonctionne.

## Correction

Retablir `path: /healthz` dans la `livenessProbe`, puis `helm upgrade`.

## Rappel theorique

* **liveness** : "faut-il redemarrer le conteneur ?" Un echec = redemarrage.
* **readiness** : "peut-on lui envoyer du trafic ?" Un echec = retrait des
  Endpoints du Service, sans redemarrage.
* **startup** : "a-t-il fini de demarrer ?" Tant qu'elle n'est pas passee,
  liveness et readiness sont suspendues. Indispensable pour les applications
  lentes (Elasticsearch ici).
* Une liveness trop stricte (ou qui vise une dependance externe) est une cause
  classique de redemarrages en cascade en production.

---

*Retour a l'etat sain : `diff -ru ../00-initial ../03` montre exactement
ce qui a ete modifie.*
