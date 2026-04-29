# Runbook - DevOps Production App

## Objectif

Ce document permet de diagnostiquer rapidement un probleme en production.

---

# 1. Verifier l'etat des conteneurs

```bash
docker-compose -f docker-compose.prod.yml ps
```

### Interpretation

* `Up` -> OK
* `Exit(1)` -> crash
* `Restarting` -> boucle de crash

---

# 2. Lire les logs

```bash
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs db
```

### En temps reel

```bash
docker-compose -f docker-compose.prod.yml logs -f backend
```

---

# 3. Tester depuis la VM

```bash
curl http://localhost/
curl http://localhost/api/health
curl http://localhost/api/users
```

### Interpretation

* OK -> le point d'entree Nginx sert bien le frontend et relaie l'API
* KO -> probleme de conteneur, de routage Nginx ou de backend

---

# 4. Verifier les ports ouverts

```bash
sudo ss -tulpn
```

### A verifier

* `0.0.0.0:80` -> frontend Nginx accessible
* pas de port backend expose publiquement
* pas de port DB expose publiquement

---

# 5. Cas de debug

## Cas 1 - Backend en `Exit(1)`

```bash
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs db
docker-compose -f docker-compose.prod.yml config
```

### Causes possibles

* Mauvais `DEVOPS_APP_DB_HOST`
* Mauvais `DEVOPS_APP_DB_USER` ou `DEVOPS_APP_DB_PASSWORD`
* Base de donnees non prete
* Bug Python
* Build backend casse

---

## Cas 2 - Frontend accessible mais API en erreur

```bash
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs backend
docker exec -it frontend sh
wget -qO- http://backend:8000/health
```

### Causes possibles

* Mauvais `proxy_pass`
* Backend non accessible depuis le frontend
* Backend down
* Mauvais port
* Route API incorrecte

---

## Cas 3 - Fonctionne dans la VM mais pas depuis Internet

### Verifier

* Security Group: port 80 ouvert
* NACL
* Route Table / Internet Gateway
* Firewall OS

---

## Cas 4 - Probleme base de donnees

```bash
docker-compose -f docker-compose.prod.yml logs db
docker-compose -f docker-compose.prod.yml logs backend
```

### Causes possibles

* DB non prete
* Mauvais credentials
* Volume corrompu
* Mauvais port

---

# 6. Commandes utiles

```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml restart
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f backend
```

---

# 7. Methode de debug

Toujours raisonner en couches:

```text
1. Frontend Nginx
2. Backend FastAPI
3. Base de donnees
4. Docker Compose
5. Machine
6. Reseau AWS
```

---

# Rappel important

* Ne jamais debug au hasard
* Toujours isoler une couche
* Toujours verifier les logs en priorite
* Toujours tester `localhost` avant Internet

---

# Conclusion

Ce runbook permet:

* d'identifier rapidement une panne
* de structurer le debug
* d'eviter les erreurs classiques
* de garder une architecture simple adaptee a une petite VM
