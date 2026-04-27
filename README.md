# DevOps Production App

Application de demonstration orientee production pour montrer comment assembler une petite stack web deployable sur une VM AWS.

Le projet est volontairement simple: un frontend statique servi par Nginx, une API FastAPI, une base PostgreSQL et une couche d'infrastructure Terraform. Il peut servir de base d'apprentissage pour des developpeurs qui veulent comprendre le chemin complet entre code applicatif, conteneurisation, orchestration locale et deploiement cloud.

## Objectifs du projet

- Montrer une architecture web lisible et facile a operer.
- Exposer une API Python avec health check, versioning et donnees persistantes.
- Servir un frontend leger adapte a une petite instance AWS `t3.micro`.
- Fournir un deploiement reproductible avec Docker Compose et Terraform.
- Documenter les gestes de debug courants via un runbook.

## Architecture

```text
Internet
   |
   v
AWS Security Group
   |
   v
EC2 Ubuntu t3.micro
   |
   v
Docker Compose
   |
   +-- frontend: Nginx
   |      |-- sert app/frontend/index.html
   |      +-- relaie /api/* vers backend:8000
   |
   +-- backend: FastAPI + Uvicorn
   |      |-- /health
   |      |-- /version
   |      |-- /users
   |      +-- connexion PostgreSQL via psycopg
   |
   +-- db: PostgreSQL 15
          +-- volume postgres-data
```

Seul le port `80` est expose publiquement. Le backend et la base de donnees restent accessibles uniquement dans le reseau Docker Compose.

## Structure du depot

```text
.
|-- app/
|   |-- backend/
|   |   |-- app/main.py          # API FastAPI et initialisation DB
|   |   |-- Dockerfile           # image Python/Uvicorn
|   |   |-- requirements.txt     # dependances backend
|   |   `-- README.md            # notes backend
|   `-- frontend/
|       |-- index.html           # interface statique
|       |-- nginx.conf           # reverse proxy /api
|       `-- Dockerfile           # image Nginx
|-- docs/
|   `-- runbook.md               # diagnostic production
|-- infra/
|   `-- terraform/               # provisionnement AWS EC2
`-- docker-compose.yml           # stack locale et production simple VM
```

## Stack technique

- **Frontend**: HTML, CSS et JavaScript sans framework.
- **Reverse proxy**: Nginx.
- **Backend**: FastAPI, Uvicorn, Pydantic Settings.
- **Base de donnees**: PostgreSQL 15.
- **Driver DB**: psycopg 3.
- **Conteneurisation**: Docker et Docker Compose.
- **Infrastructure**: Terraform pour creer l'instance EC2, la cle SSH et le security group.

## Demarrage rapide avec Docker Compose

Prerequis:

- Docker
- Docker Compose

Depuis la racine du projet:

```bash
docker-compose up -d --build
```

Verifier les services:

```bash
docker-compose ps
curl http://localhost/
curl http://localhost/api/health
curl http://localhost/api/users
```

Arreter la stack:

```bash
docker-compose down
```

Supprimer aussi les donnees PostgreSQL locales:

```bash
docker-compose down -v
```

## API backend

Le backend expose les routes suivantes dans le conteneur sur le port `8000`. Depuis l'exterieur de la stack, elles passent par Nginx avec le prefixe `/api`.

| Route publique | Route backend | Description |
| --- | --- | --- |
| `/api/health` | `/health` | Etat applicatif et statut de connexion DB |
| `/api/version` | `/version` | Version et environnement de l'application |
| `/api/users` | `/users` | Liste des utilisateurs seedes au demarrage |
| `/api/users/{id}` | `/users/{id}` | Detail d'un utilisateur |

Au demarrage, l'application:

1. attend que PostgreSQL soit disponible;
2. cree ou met a jour la table `users`;
3. insere des utilisateurs de demonstration si la table est vide.

## Configuration

Le backend lit sa configuration via des variables d'environnement prefixees par `DEVOPS_APP_`.

| Variable | Valeur par defaut | Role |
| --- | --- | --- |
| `DEVOPS_APP_APP_ENV` | `development` | Nom de l'environnement |
| `DEVOPS_APP_LOG_LEVEL` | `INFO` | Niveau de logs Python |
| `DEVOPS_APP_DB_HOST` | `localhost` | Hote PostgreSQL |
| `DEVOPS_APP_DB_PORT` | `5432` | Port PostgreSQL |
| `DEVOPS_APP_DB_NAME` | `devdb` | Nom de la base |
| `DEVOPS_APP_DB_USER` | `devuser` | Utilisateur DB |
| `DEVOPS_APP_DB_PASSWORD` | `devpass` | Mot de passe DB |
| `DEVOPS_APP_DB_CONNECT_TIMEOUT` | `5` | Timeout de connexion DB |
| `DEVOPS_APP_DB_INIT_RETRIES` | `10` | Nombre d'essais d'initialisation DB |
| `DEVOPS_APP_DB_INIT_RETRY_DELAY_SECONDS` | `3` | Delai entre les essais |

Dans `docker-compose.yml`, ces variables sont deja renseignees pour faire communiquer le backend avec le service `db`.

## Developpement backend sans Docker

Depuis `app/backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Pour utiliser PostgreSQL via Docker tout en lancant le backend localement, demarrer uniquement la base:

```bash
docker-compose up -d db
```

Puis configurer le backend pour joindre `localhost:5432`.

## Deploiement AWS avec Terraform

Le dossier [infra/terraform](infra/terraform) provisionne:

- une instance EC2 Ubuntu 22.04;
- un security group avec HTTP public et SSH restreint;
- une key pair AWS;
- un script `user_data.sh` qui installe Docker, clone le depot et lance Docker Compose.

Usage:

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

Apres l'application, Terraform affiche l'adresse IP publique et une commande SSH prete a l'emploi.

## Operations et debug

Les commandes de diagnostic sont regroupees dans [docs/runbook.md](docs/runbook.md).

Commandes utiles:

```bash
docker-compose ps
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
docker-compose restart
```

Pour diagnostiquer proprement, suivre les couches dans cet ordre:

```text
Frontend Nginx -> Backend FastAPI -> PostgreSQL -> Docker Compose -> VM -> Reseau AWS
```

## Pistes de contribution

Idees d'amelioration pour developpeurs interesses:

- Ajouter des tests automatises backend avec `pytest` et `httpx`.
- Ajouter une pipeline CI GitHub Actions pour lint, tests et build Docker.
- Remplacer les credentials de demonstration par une gestion de secrets adaptee.
- Ajouter des migrations de schema avec Alembic.
- Ajouter des endpoints CRUD pour les utilisateurs.
- Ajouter des probes Docker healthcheck.
- Publier les images dans un registry au lieu de builder directement sur la VM.
- Ajouter HTTPS via un reverse proxy avec certificats.

## Documents associes

- [Runbook production](docs/runbook.md)
- [README backend](app/backend/README.md)
- [README Terraform](infra/terraform/README.md)
