# Exercice 7 - Une 503 qui n'apparait que dans les logs

| | |
|---|---|
| **Difficulte** | ***.. |
| **Duree indicative** | 15 min |
| **Chart** | copie de `v2/00-initial` avec une panne introduite |

## Mise en place

```bash
cd v2/07
helm upgrade --install monchart . -n <prenom>-tshoot
```

## Contexte

Apres une modification de la configuration du frontend, la page d'accueil
affiche `backend : injoignable (503...)`. Cette fois, le Service backend a bien
des Endpoints et les pods backend repondent correctement quand on les teste
directement.

## Ce que vous devez constater

* `kubectl get endpoints service-backend-clusterip` : les adresses sont la
* interroge directement, le **backend** repond parfaitement :
  `kubectl port-forward svc/service-backend-clusterip 8080:80` puis
  `curl http://localhost:8080/whoami`
* seul le passage par `/api/` du frontend renvoie une 503

## Votre mission

Trouver pourquoi le frontend n'arrive pas a joindre le backend, alors que tout
le monde va bien.

## Questions pour vous guider

* Quand une application se plaint sans le dire a l'utilisateur, ou ecrit-elle ?
  `kubectl logs -l tier=frontend --tail=20`
* Que raconte exactement le message d'erreur nginx ? Notez l'adresse **et** le
  port.
* Sur quel port le Service backend ecoute-t-il ?
  `kubectl get svc service-backend-clusterip`
* Quelle est la difference entre le `port` d'un Service et le `targetPort` ?

## Critere de reussite

`curl http://<node>:<port-frontend>/api/whoami` renvoie l'identite d'un pod
backend, et les pastilles de la page repassent au vert.

---

*Le fichier `corrige.md` de ce dossier contient la solution : ne l'ouvrez
qu'apres avoir trouve, ou si vous etes vraiment bloque.*
