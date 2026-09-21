# Corrigé - exercice 11 : Des pods évincés les uns après les autres

| | |
|---|---|
| **Panne** | `ephemeral-storage` du frontend passé à `1Ki` (confusion d'unités) |
| **Fichier(s) modifié(s)** | `values.yaml` |
| **Symptôme attendu** | pods frontend `Evicted` les uns après les autres |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

`values.yaml`, tier frontend : confusion d'unités, `1Ki` au lieu de `1Gi`.

```diff
     requests:
-      ephemeral-storage: "128M"
+      ephemeral-storage: "1Ki"
     limits:
-      ephemeral-storage: "512M"
+      ephemeral-storage: "1Ki"
```

1 Ki, c'est moins qu'un seul bloc de système de fichiers : le conteneur dépasse
la limite des qu'il écrit quoi que ce soit (nginx crée son fichier de PID et
ses répertoires de cache au démarrage).

## Démarche de diagnostic

```bash
kubectl -n <ns> get pods -l tier=frontend
# NAME                                   READY   STATUS    RESTARTS   AGE
# deployment-frontend-6c7d8f9b4-2xk4m    0/1     Evicted   0          30s
# deployment-frontend-6c7d8f9b4-7lmnp    0/1     Evicted   0          70s
# ...

kubectl -n <ns> describe pod <pod-evicted> | head -20
#   Status:   Failed
#   Reason:   Evicted
#   Message:  Pod ephemeral local storage usage exceeds the total limit of containers 1Ki.
```

C'est **kubelet** (le gestionnaire d'éviction), pas le scheduler ni le noyau.
Il mesure périodiquement ce que le pod consomme en stockage éphémère et le tue
s'il dépasse sa limite.

Le stockage éphémère compte : la couche d'écriture du conteneur, les volumes
`emptyDir`, et les logs du conteneur sur le noeud. Il ne compte **pas** les
volumes persistants : `pvc-reports` n'a rien à voir ici.

## Correction

Rétablir `128M` en requests et `512M` en limits pour le frontend, puis
`helm upgrade`. Nettoyage des pods morts :

```bash
kubectl -n <ns> delete pods --field-selector=status.phase=Failed
```

## Rappel théorique

* `Evicted` = décision de kubelet ; le pod est en phase `Failed`, son
  contrôleur en recrée un autre, d'où l'accumulation.
* `OOMKilled` = décision du noyau sur la mémoire d'un conteneur ; le conteneur
  redémarre dans le même pod, le compteur `RESTARTS` augmente.
* Piège : une limite de stockage éphémère trop petite mais pas absurde (par
  exemple 50 Mi) ne se manifeste qu'au bout de plusieurs heures, quand les logs
  ont grossi. Bien plus difficile à diagnostiquer que ce cas-ci.
* Les logs applicatifs volumineux se traitent par une rotation côté noeud, pas
  en supprimant la limite.

---

*Retour à l'état sain : `diff -ru ../00-initial ../11` montre exactement
ce qui a été modifié.*
