# Corrige - exercice 2 : Le tier backend redemarre en boucle

| | |
|---|---|
| **Panne** | directive nginx `autoindex_on;` au lieu de `autoindex on;` |
| **Fichier(s) modifie(s)** | `templates/configmap-backend.yaml` |
| **Symptome attendu** | pods backend en `CrashLoopBackOff` |

> A ne pas distribuer aux etudiants avant la fin de l'exercice.

## La panne injectee

`templates/configmap-backend.yaml`, bloc `location /reports/` :

```diff
-            autoindex on;
+            autoindex_on;
```

`autoindex_on` n'est pas une directive nginx : le processus refuse de demarrer.

## Demarche de diagnostic

```bash
kubectl -n <ns> get pods -l tier=backend
# NAME                                  READY   STATUS             RESTARTS
# deployment-backend-7d9c45b8f-4mrp5    0/1     CrashLoopBackOff   4 (30s ago)

kubectl -n <ns> logs -l tier=backend --previous --tail=10
# nginx: [emerg] unknown directive "autoindex_on" in /etc/nginx/conf.d/default.conf:41
```

Le conteneur est mort : `kubectl logs` sans option affiche les logs du
conteneur *courant* (qui vient peut-etre de redemarrer et n'a rien ecrit).
`--previous` affiche ceux de l'instance precedente, celle qui a plante.

Le fichier est monte depuis le ConfigMap `configmap-backend` :

```bash
kubectl -n <ns> get cm configmap-backend -o jsonpath='{.data.default\.conf}' | grep -n autoindex
```

## Correction

Retablir `autoindex on;` dans `templates/configmap-backend.yaml`, puis
`helm upgrade`. Les pods redemarrent tout seuls grace a l'annotation
`checksum/configmap-backend` du Deployment.

## Rappel theorique

* `CrashLoopBackOff` n'est pas une erreur en soi : c'est kubelet qui espace les
  redemarrages (10 s, 20 s, 40 s... jusqu'a 5 min) d'un conteneur qui sort.
* Reflexe : `kubectl logs --previous`, puis `kubectl describe pod` pour le code
  de sortie (`Exit Code`) et la raison (`Reason`).
* Un conteneur qui sort en erreur immediatement = probleme de configuration ou
  de binaire ; un conteneur tue plus tard = plutot une sonde ou une limite.

---

*Retour a l'etat sain : `diff -ru ../00-initial ../02` montre exactement
ce qui a ete modifie.*
