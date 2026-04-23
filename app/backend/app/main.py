import logging
import os
import time

import psycopg
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DevOps Production App",
    version="1.0.0",
)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "devdb")
DB_USER = os.getenv("DB_USER", "devuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "devpass")


def get_db_connection():
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def init_db() -> None:
    logger.info("Initializing database")
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
        """
    )

    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]

    if count == 0:
        logger.info("Seeding initial users")
        cur.execute(
            """
            INSERT INTO users (name)
            VALUES
                ('Alice'),
                ('Bob'),
                ('Charlie')
            """
        )

    conn.commit()
    cur.close()
    conn.close()


@app.on_event("startup")
def startup_event() -> None:
    max_retries = 10
    delay_seconds = 3

    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Attempt %s/%s to initialize database", attempt, max_retries)
            init_db()
            logger.info("Database initialized successfully")
            return
        except Exception as exc:
            logger.warning(
                "Database initialization failed on attempt %s/%s: %s",
                attempt,
                max_retries,
                exc,
            )
            time.sleep(delay_seconds)

    raise RuntimeError("Could not initialize database after multiple attempts")


@app.get("/health")
def health() -> dict[str, str]:
    logger.info("Health endpoint called")
    return {"status": "ok"}


@app.get("/users")
def get_users() -> dict[str, list[dict[str, object]]]:
    logger.info("Users endpoint called")
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM users ORDER BY id")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    users = [{"id": row[0], "name": row[1]} for row in rows]
    return {"users": users}


@app.get("/version")
def version() -> dict[str, str]:
    logger.info("Version endpoint called")
    return {"version": "1.0.0"}