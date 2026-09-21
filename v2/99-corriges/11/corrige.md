# Corrigé - exercice 11 : Des pods évincés les uns après les autres

| | |
|---|---|
| **Panne** | `ephemeral-storage` du frontend passé à `1Ki` (confusion d'unités) |
| **Fichier(s) modifié(s)** | `values.yaml` |
| **Symptôme attendu** | pods frontend arrêtés par kubelet les uns après les autres, affichés `Completed` |

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
la limite dès qu'il écrit quoi que ce soit (nginx crée son fichier de PID et
ses répertoires de cache au démarrage).

## Démarche de diagnostic

```bash
kubectl -n <ns> get pods -l tier=frontend
# NAME                                   READY   STATUS      RESTARTS   AGE
# deployment-frontend-5cbbd99669-652x6   0/1     Completed   0          70s
# deployment-frontend-5cbbd99669-c7kw9   0/1     Completed   0          55s
# deployment-frontend-5cbbd99669-22lz7   0/1     Completed   0          14s
# deployment-frontend-5d965dc5f-6qfvd    1/1     Running     0          2h   <- l'ancien, qui sert
```

Premier réflexe : **un pod géré par un Deployment ne se termine jamais tout
seul**. Ses conteneurs sont censés tourner indéfiniment ; un `Completed` sur
une telle charge de travail est toujours anormal.

Le statut du pod, lui, ne dit rien :

```bash
kubectl -n <ns> get pod <pod> \
  -o custom-columns='PHASE:.status.phase,RAISON:.status.reason,MESSAGE:.status.message'
# PHASE       RAISON   MESSAGE
# Succeeded   <none>   <none>
```

Tout est dans les **événements** :

```bash
kubectl -n <ns> describe pod <pod> | tail -8
# Events:
#   Normal   Scheduled  14s  default-scheduler  Successfully assigned ...
#   Normal   Pulled     13s  kubelet            Container image ... already present on machine
#   Normal   Created    13s  kubelet            Created container: frontend-container
#   Normal   Started    13s  kubelet            Started container frontend-container
#   Warning  Evicted    13s  kubelet            Pod ephemeral local storage usage exceeds the total limit of containers 1Ki.
#   Normal   Killing    11s  kubelet            Stopping container frontend-container
```

C'est **kubelet** (son gestionnaire d'éviction), pas le scheduler ni le noyau.
Il mesure périodiquement ce que le pod consomme en stockage éphémère et le tue
dès qu'il dépasse sa limite : ici, une dizaine de secondes après le démarrage.

Pourquoi `Completed` et pas `Evicted` ? Parce que kubelet arrête le conteneur
**proprement** (SIGTERM), et que nginx sort en 0. Selon la version de
Kubernetes, le motif d'éviction n'est pas recopié dans `status.reason` du pod,
et la colonne STATUS affiche alors le résultat du conteneur. L'**événement**,
lui, est toujours présent.

Le stockage éphémère compte : la couche d'écriture du conteneur, les volumes
`emptyDir`, et les logs du conteneur sur le noeud. Il ne compte **pas** les
volumes persistants : `pvc-reports` n'a rien à voir ici.

## Correction

Rétablir `128M` en requests et `512M` en limits pour le frontend, puis
`helm upgrade`. Nettoyage des pods morts :

```bash
kubectl -n <ns> delete pods --field-selector=status.phase=Failed
kubectl -n <ns> delete pods --field-selector=status.phase=Succeeded
```

Deux commandes, parce que selon le cas ces pods sont en phase `Failed`
(`Evicted`) ou `Succeeded` (`Completed`).

## Rappel théorique

* Une **éviction** est une décision de kubelet, pas du scheduler ni du noyau.
  Le pod n'est pas redémarré : son contrôleur en recrée un autre, d'où
  l'accumulation de cadavres.
* Selon la version de Kubernetes, l'éviction apparaît dans `status.reason`
  (phase `Failed`, affichée `Evicted`) **ou seulement dans les événements**
  (phase `Succeeded`, affichée `Completed`). Ne jamais se fier à la seule
  colonne STATUS de `kubectl get pods`.
* Les événements ne sont conservés qu'une heure par défaut. Passé ce délai,
  `describe` ne montre plus rien et le pod mort n'a plus aucune explication :
  sur un incident de la nuit, il est souvent trop tard. C'est la raison d'être
  des collecteurs d'événements.
* `OOMKilled` = décision du noyau sur la mémoire d'un conteneur ; le conteneur
  redémarre dans le même pod, le compteur `RESTARTS` augmente.
* Piège : une limite de stockage éphémère trop petite mais pas absurde (par
  exemple 50 Mi) ne se manifeste qu'au bout de plusieurs heures, quand les logs
  ont grossi. Bien plus difficile à diagnostiquer que ce cas-ci.
* Les logs applicatifs volumineux se traitent par une rotation côté noeud, pas
  en supprimant la limite.

---

*Retour à l'état sain : `diff -ru ../../00-initial ../../11` montre exactement
ce qui a été modifié.*
