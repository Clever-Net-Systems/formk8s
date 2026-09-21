# Corrigé - exercice 10 : Un Job qui ne crée aucun pod

| | |
|---|---|
| **Panne** | Job `job-purge` ajouté, non conforme au profil `restricted` (root, escalade autorisée, seccomp et capabilities absents) |
| **Fichier(s) modifié(s)** | `templates/job-purge.yml` (ajouté) |
| **Symptôme attendu** | le Job existe, aucun pod n'est jamais créé |

> À ne pas distribuer aux étudiants avant la fin de l'exercice.

## La panne injectée

Ajout de `templates/job-purge.yml`, dont le pod viole le profil `restricted` à
quatre titres :

```yaml
      securityContext:
        runAsUser: 0            # root
      # runAsNonRoot absent
      # seccompProfile absent
          securityContext:
            allowPrivilegeEscalation: true   # interdit
            # capabilities.drop: ["ALL"] absent
```

## Démarche de diagnostic

Le point clé : **l'admission refuse la création du pod, pas celle du Job**.
Le Job est donc bien créé, et c'est son contrôleur qui échoue en boucle.

```bash
kubectl -n <ns> get jobs
# NAME        STATUS    COMPLETIONS   DURATION   AGE
# job-purge   Running   0/1                      3m

kubectl -n <ns> describe job job-purge | tail -12
#   Warning  FailedCreate  ... Error creating: pods "job-purge-" is forbidden:
#   violates PodSecurity "restricted:latest":
#     allowPrivilegeEscalation != false (container "purge-container" must set
#       securityContext.allowPrivilegeEscalation=false),
#     unrestricted capabilities (container "purge-container" must set
#       securityContext.capabilities.drop=["ALL"]),
#     runAsNonRoot != true, runAsUser=0, seccompProfile
```

Le message donne la liste complète de ce qui manque. On peut aussi le retrouver
dans les événements du namespace :

```bash
kubectl -n <ns> get events --sort-by=.lastTimestamp | grep -i forbidden | tail -3
```

## Correction

Aligner le Job sur ce que fait déjà le CronJob du chart, dans
`templates/job-purge.yml` :

```yaml
      securityContext:
        runAsNonRoot: true
        runAsUser: 65534
        runAsGroup: 65534
        fsGroup: 2000            # pour ecrire sur le volume partage
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: purge-container
          securityContext:
            allowPrivilegeEscalation: false
            capabilities:
              drop:
                - ALL
```

Abaisser le namespace en `baseline` ferait disparaître le message, mais
reviendrait à supprimer le garde-fou pour toute l'application : la règle est de
corriger la charge de travail, pas la politique.

## Rappel théorique

* Pod Security Admission travaille **à la création du pod**. Pour tout objet qui
  crée des pods (Deployment, Job, CronJob, StatefulSet), le message d'erreur se
  trouve sur le ReplicaSet / le Job, jamais sur un pod qui n'existe pas.
* Trois modes, cumulables par namespace : `enforce` (refuse), `audit` (journal),
  `warn` (avertissement dans la sortie kubectl).
* Le profil `restricted` exige au minimum : `runAsNonRoot: true`,
  `allowPrivilegeEscalation: false`, `capabilities.drop: ["ALL"]`,
  `seccompProfile.type: RuntimeDefault`, et des types de volumes limites.
* Avec `warn` actif, `kubectl apply` d'un manifeste non conforme affiche
  l'avertissement tout de suite : c'est le moyen le plus rapide de tester.

---

*Retour à l'état sain : `diff -ru ../00-initial ../10` montre exactement
ce qui a été modifié.*
