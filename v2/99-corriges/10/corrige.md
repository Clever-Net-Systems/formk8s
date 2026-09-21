# Corrigé - exercice 10 : Un Job qui ne crée aucun pod

| | |
|---|---|
| **Panne** | Job `job-purge` ajouté, avec `runAsNonRoot: false` : une seule ligne le rend non conforme au profil `restricted` |
| **Fichier(s) modifié(s)** | `templates/job-purge.yml` (ajouté) |
| **Symptôme attendu** | le Job existe, aucun pod n'est jamais créé |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

Ajout de `templates/job-purge.yml`. Le pod respecte le profil `restricted` sur
tous les points — seccomp, capabilities, escalade de privilèges, UID non-root —
sauf **un seul** :

```yaml
      securityContext:
        runAsNonRoot: false      # <- le seul point bloquant
        runAsUser: 65534         # (pourtant bien un UID non-root)
        runAsGroup: 65534
        fsGroup: 2000
        seccompProfile:
          type: RuntimeDefault
```

Le conteneur tournerait donc réellement en non-root. Mais Pod Security
Admission ne regarde pas ce que fait l'image : il vérifie ce que le manifeste
**déclare**. Tant que `runAsNonRoot` n'est pas à `true`, le pod est refusé.

## Démarche de diagnostic

Le point clé : **l'admission refuse la création du pod, pas celle du Job**.
Le Job est donc bien créé, et c'est son contrôleur qui échoue en boucle.

```bash
kubectl -n <ns> get jobs
# NAME        STATUS    COMPLETIONS   DURATION   AGE
# job-purge   Running   0/1                      3m

kubectl -n <ns> describe job job-purge | tail -12
#   Warning  FailedCreate  ... Error creating: pods "job-purge-xxxxx" is forbidden:
#   violates PodSecurity "restricted:latest": runAsNonRoot != true
#   (pod must not set securityContext.runAsNonRoot=false)
```

Le message nomme exactement le champ fautif. On peut aussi le retrouver dans
les événements du namespace :

```bash
kubectl -n <ns> get events --sort-by=.lastTimestamp | grep -i forbidden | tail -3
```

## Correction

Une seule ligne, dans `templates/job-purge.yml` :

```diff
       securityContext:
-        runAsNonRoot: false
+        runAsNonRoot: true
```

puis `helm upgrade`. Le Job crée alors son pod, qui se termine en quelques
secondes.

Abaisser le namespace en `baseline` ferait disparaître le message, mais
reviendrait à supprimer le garde-fou pour toute l'application : la règle est de
corriger la charge de travail, pas la politique.

## Rappel théorique

* Pod Security Admission travaille **à la création du pod**. Pour tout objet qui
  crée des pods (Deployment, Job, CronJob, StatefulSet), le message d'erreur se
  trouve sur le ReplicaSet / le Job, jamais sur un pod qui n'existe pas.
* Trois modes, cumulables par namespace : `enforce` (refuse), `audit` (journal),
  `warn` (avertissement dans la sortie kubectl).
* Pod Security Admission est **déclaratif** : il lit le manifeste, il
  n'inspecte pas l'image. Un conteneur qui tournerait en non-root est quand
  même refusé s'il ne le déclare pas.
* Le profil `restricted` exige au minimum : `runAsNonRoot: true`,
  `allowPrivilegeEscalation: false`, `capabilities.drop: ["ALL"]`,
  `seccompProfile.type: RuntimeDefault`, et des types de volumes limites.
* Avec `warn` actif, `kubectl apply` d'un manifeste non conforme affiche
  l'avertissement tout de suite : c'est le moyen le plus rapide de tester.

---

*Retour à l'état sain : `diff -ru ../../00-initial ../../10` montre exactement
ce qui a été modifié.*
