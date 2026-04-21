from fastapi import FastAPI

# Création de l'application
app = FastAPI(
    title="DevOps Production App",
    version="1.0.0"
)

# Endpoint de santé (très important en prod)
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

# Endpoint métier simple
@app.get("/users")
def get_users() -> dict:
    return {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    }

# Endpoint de version (très utilisé en prod)
@app.get("/version")
def version() -> dict[str, str]:
    return {"version": "1.0.0"}