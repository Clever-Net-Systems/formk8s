# monchart - chart de référence des TP de troubleshooting

Chart Helm **volontairement sain** : c'est la version qui fonctionne, celle à laquelle on compare les versions cassées (`../1`, `../2`, ...).

**La description complète du déploiement (architecture, rôle de chaque tier,
objets créés, prérequis, choix liés au namespace `restricted`, pièges connus)
est dans [`../99-corriges/README.md`](../99-corriges/README.md).**

## Fichiers

| Fichier | Rôle |
|---|---|
| `values.yaml` | **le seul** fichier de valeurs, déjà fonctionnel tel quel |
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
