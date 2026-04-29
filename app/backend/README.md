# DevOps Production App

## Backend

Backend FastAPI de l'application. Il expose des endpoints de monitoring et une ressource `users` stockee dans PostgreSQL.

## Responsabilites

- Charger la configuration via les variables `DEVOPS_APP_*`.
- Initialiser la table `users` au demarrage.
- Seeder des utilisateurs de demonstration si la table est vide.
- Exposer des reponses JSON validees par Pydantic.
- Journaliser chaque requete HTTP.

## Endpoints

| Methode | Route | Description |
| --- | --- | --- |
| `GET` | `/health` | Etat du service et de la base PostgreSQL |
| `GET` | `/version` | Version et environnement courant |
| `GET` | `/users` | Liste des utilisateurs |
| `GET` | `/users/{user_id}` | Detail d'un utilisateur |

## Setup local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Par defaut, le backend cherche PostgreSQL sur `localhost:5432` avec:

```text
database: devdb
user: devuser
password: devpass
```

Pour lancer uniquement PostgreSQL depuis la racine du depot:

```bash
docker compose -f docker-compose.dev.yml up -d db
```

## Variables utiles

| Variable | Description |
| --- | --- |
| `DEVOPS_APP_APP_ENV` | Environnement affiche par `/health` et `/version` |
| `DEVOPS_APP_LOG_LEVEL` | Niveau de logs |
| `DEVOPS_APP_DB_HOST` | Hote PostgreSQL |
| `DEVOPS_APP_DB_PORT` | Port PostgreSQL |
| `DEVOPS_APP_DB_NAME` | Nom de la base |
| `DEVOPS_APP_DB_USER` | Utilisateur PostgreSQL |
| `DEVOPS_APP_DB_PASSWORD` | Mot de passe PostgreSQL |

## Execution avec Docker

Depuis la racine du depot:

```bash
docker compose -f docker-compose.dev.yml up -d --build backend db
```
