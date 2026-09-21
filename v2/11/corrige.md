# Corrige - exercice 11 : Des pods evinces les uns apres les autres

| | |
|---|---|
| **Panne** | `ephemeral-storage` du frontend passe a `1Ki` (confusion d'unites) |
| **Fichier(s) modifie(s)** | `values.yaml` |
| **Symptome attendu** | pods frontend `Evicted` les uns apres les autres |

> A ne pas distribuer aux etudiants avant la fin de l'exercice.

## La panne injectee

`values.yaml`, tier frontend : confusion d'unites, `1Ki` au lieu de `1Gi`.

```diff
     requests:
-      ephemeral-storage: "128M"
+      ephemeral-storage: "1Ki"
     limits:
-      ephemeral-storage: "512M"
+      ephemeral-storage: "1Ki"
```

1 Ki, c'est moins qu'un seul bloc de systeme de fichiers : le conteneur depasse
la limite des qu'il ecrit quoi que ce soit (nginx cree son fichier de PID et
ses repertoires de cache au demarrage).

## Demarche de diagnostic

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

C'est **kubelet** (le gestionnaire d'eviction), pas le scheduler ni le noyau.
Il mesure periodiquement ce que le pod consomme en stockage ephemere et le tue
s'il depasse sa limite.

Le stockage ephemere compte : la couche d'ecriture du conteneur, les volumes
`emptyDir`, et les logs du conteneur sur le noeud. Il ne compte **pas** les
volumes persistants : `pvc-reports` n'a rien a voir ici.

## Correction

Retablir `128M` en requests et `512M` en limits pour le frontend, puis
`helm upgrade`. Nettoyage des cadavres :

```bash
kubectl -n <ns> delete pods --field-selector=status.phase=Failed
```

## Rappel theorique

* `Evicted` = decision de kubelet ; le pod est en phase `Failed`, son
  controleur en recree un autre, d'ou l'accumulation.
* `OOMKilled` = decision du noyau sur la memoire d'un conteneur ; le conteneur
  redemarre dans le meme pod, le compteur `RESTARTS` augmente.
* Piege : une limite de stockage ephemere trop petite mais pas absurde (par
  exemple 50 Mi) ne se manifeste qu'au bout de plusieurs heures, quand les logs
  ont grossi. Bien plus difficile a diagnostiquer que ce cas-ci.
* Les logs applicatifs volumineux se traitent par une rotation cote noeud, pas
  en supprimant la limite.

---

*Retour a l'etat sain : `diff -ru ../00-initial ../11` montre exactement
ce qui a ete modifie.*
