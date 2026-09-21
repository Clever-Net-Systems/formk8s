# Corrige - exercice 7 : Une 503 qui n'apparait que dans les logs

| | |
|---|---|
| **Panne** | `proxy_pass` du frontend vers le port `8080` (port du conteneur) au lieu de `80` (port du Service) |
| **Fichier(s) modifie(s)** | `templates/configmap-frontend.yaml` |
| **Symptome attendu** | 503 sur `/api/` uniquement, backend sain par ailleurs |

> A ne pas distribuer aux etudiants avant la fin de l'exercice.

## La panne injectee

`templates/configmap-frontend.yaml`, directive `proxy_pass` :

```diff
-            proxy_pass  http://service-backend-clusterip.<ns>.svc.cluster.local:80/;
+            proxy_pass  http://service-backend-clusterip.<ns>.svc.cluster.local:8080/;
```

8080 est le port du **conteneur** (`targetPort`), pas celui du **Service**
(`port: 80`). Le Service n'ecoute pas sur 8080 : la connexion est refusee.

## Demarche de diagnostic

```bash
kubectl -n <ns> logs -l tier=frontend --tail=20
# [error] connect() failed (111: Connection refused) while connecting to upstream,
#   upstream: "http://10.43.12.34:8080/whoami", host: "..."
```

Tout est dans cette ligne : l'IP est bien celle du Service (ClusterIP), mais le
port est faux. Verification :

```bash
kubectl -n <ns> get svc service-backend-clusterip
# NAME                        TYPE        CLUSTER-IP     PORT(S)
# service-backend-clusterip   ClusterIP   10.43.12.34    80/TCP
```

Le Service expose 80 et redirige vers le port 8080 du conteneur. Un client,
lui, doit taper sur **80**.

## Correction

Retablir `:{{ .Values.backend.service.port }}/` (soit 80) dans `proxy_pass`,
puis `helm upgrade`. Les pods frontend redemarrent grace au `checksum/`.

## Rappel theorique

* `port` = le port du Service (ce que les clients appellent).
  `targetPort` = le port du conteneur (ou le nom du port declare dans le pod,
  `http` ici). `nodePort` = le port ouvert sur chaque noeud.
* Le Service du backend est de type `ClusterIP` : il n'existe qu'a l'interieur
  du cluster et n'est joignable que par son nom DNS. C'est le cas le plus
  courant pour un service interne. Le Service du frontend, lui, est un
  `NodePort` : un **sur-ensemble** du ClusterIP, avec en plus une porte ouverte
  sur chaque noeud pour les clients externes. Dans les deux cas, un client
  interne passe par le ClusterIP : c'est visible dans le message d'erreur
  ci-dessus, l'adresse est un `10.x`, pas une IP de noeud.
* Nommer les ports du conteneur et referencer ce nom dans `targetPort` evite ce
  genre d'erreur du cote Service... mais pas dans une configuration applicative,
  qui ne connait que le port du Service.
* Reflexe : une 502/503 rendue par un reverse-proxy raconte toujours son echec
  dans les logs du proxy, pas dans ceux du service cible.

---

*Retour a l'etat sain : `diff -ru ../00-initial ../07` montre exactement
ce qui a ete modifie.*
