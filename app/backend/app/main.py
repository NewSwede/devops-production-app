import logging
from fastapi import FastAPI

# configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DevOps Production App",
    version="1.0.0"
)

@app.get("/health")
def health():
    logger.info("Health endpoint called")
    return {"status": "ok"}

@app.get("/users")
def get_users():
    logger.info("Users endpoint called")
    return {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    }

@app.get("/version")
def version():
    logger.info("Version endpoint called")
    return {"version": "1.0.0"}