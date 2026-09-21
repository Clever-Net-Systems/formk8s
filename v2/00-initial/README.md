# monchart - chart de reference des TP de troubleshooting

Chart Helm **volontairement sain** : c'est la version qui fonctionne, celle a
laquelle on compare les versions cassees (`../1`, `../2`, ...).

**La description complete du deploiement (architecture, role de chaque tier,
objets crees, prerequis, choix lies au namespace `restricted`, pieges connus)
est dans [`../README.md`](../README.md).**

## Fichiers

| Fichier | Role |
|---|---|
| `values.yaml` | **le seul** fichier de valeurs, deja fonctionnel tel quel |
| `templates/` | 4 charges de travail, 3 Services, 1 PVC, 5 ConfigMap/Secret, 1 test |

## Installation

```bash
helm upgrade --install monchart . -n <prenom>-tshoot

helm test monchart -n <prenom>-tshoot --logs
```

## Rendu sans installer

```bash
helm template monchart . -n <prenom>-tshoot | less
helm lint .
```
