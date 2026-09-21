# Corrige - exercice 10 : Un Job qui ne cree aucun pod

| | |
|---|---|
| **Panne** | Job `job-purge` ajoute, non conforme au profil `restricted` (root, escalade autorisee, seccomp et capabilities absents) |
| **Fichier(s) modifie(s)** | `templates/job-purge.yml` (ajoute) |
| **Symptome attendu** | le Job existe, aucun pod n'est jamais cree |

> A ne pas distribuer aux etudiants avant la fin de l'exercice.

## La panne injectee

Ajout de `templates/job-purge.yml`, dont le pod viole le profil `restricted` a
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

## Demarche de diagnostic

Le point cle : **l'admission refuse la creation du pod, pas celle du Job**.
Le Job est donc bien cree, et c'est son controleur qui echoue en boucle.

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

Le message donne la liste complete de ce qui manque. On peut aussi le retrouver
dans les evenements du namespace :

```bash
kubectl -n <ns> get events --sort-by=.lastTimestamp | grep -i forbidden | tail -3
```

## Correction

Aligner le Job sur ce que fait deja le CronJob du chart, dans
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

Abaisser le namespace en `baseline` ferait disparaitre le message, mais
reviendrait a supprimer le garde-fou pour toute l'application : la regle est de
corriger la charge de travail, pas la politique.

## Rappel theorique

* Pod Security Admission travaille **a la creation du pod**. Pour tout objet qui
  cree des pods (Deployment, Job, CronJob, StatefulSet), le message d'erreur se
  trouve sur le ReplicaSet / le Job, jamais sur un pod qui n'existe pas.
* Trois modes, cumulables par namespace : `enforce` (refuse), `audit` (journal),
  `warn` (avertissement dans la sortie kubectl).
* Le profil `restricted` exige au minimum : `runAsNonRoot: true`,
  `allowPrivilegeEscalation: false`, `capabilities.drop: ["ALL"]`,
  `seccompProfile.type: RuntimeDefault`, et des types de volumes limites.
* Avec `warn` actif, `kubectl apply` d'un manifeste non conforme affiche
  l'avertissement tout de suite : c'est le moyen le plus rapide de tester.

---

*Retour a l'etat sain : `diff -ru ../00-initial ../10` montre exactement
ce qui a ete modifie.*
