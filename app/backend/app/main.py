import logging
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Generator

import psycopg
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from psycopg.rows import dict_row


class Settings(BaseSettings):
    app_name: str = "DevOps Production App"
    app_version: str = "1.2.0"
    app_env: str = "development"
    log_level: str = "INFO"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "devdb"
    db_user: str = "devuser"
    db_password: str = "devpass"
    db_connect_timeout: int = 5
    db_init_retries: int = 10
    db_init_retry_delay_seconds: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DEVOPS_APP_",
        extra="ignore",
    )


settings = Settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("devops-production-app")


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str
    timestamp: datetime


class User(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    role: str = Field(min_length=1, max_length=100)
    team: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=300)
    is_active: bool
    created_at: datetime


class UsersResponse(BaseModel):
    users: list[User]
    total: int


class VersionResponse(BaseModel):
    version: str
    environment: str


class ErrorResponse(BaseModel):
    detail: str


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Small production-oriented FastAPI service backed by PostgreSQL.",
)
app.state.started_at = datetime.now(UTC)


def get_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        connect_timeout=settings.db_connect_timeout,
        row_factory=dict_row,
    )


@contextmanager
def db_cursor() -> Generator[psycopg.Cursor, None, None]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            yield cur


def check_database() -> bool:
    try:
        with db_cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        return True
    except Exception:
        logger.exception("Database health check failed")
        return False


def ensure_user_schema(cur: psycopg.Cursor) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
        """
    )

    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255)")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(100)")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS team VARCHAR(100)")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS description VARCHAR(300)")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ")

    cur.execute(
        """
        UPDATE users
        SET
            email = COALESCE(email, LOWER(REPLACE(name, ' ', '.')) || '@example.com'),
            role = COALESCE(role, 'platform-engineer'),
            team = COALESCE(team, 'platform'),
            description = COALESCE(
                description,
                'Contributes to the platform team and supports production operations.'
            ),
            is_active = COALESCE(is_active, TRUE),
            created_at = COALESCE(created_at, NOW())
        """
    )

    cur.execute("ALTER TABLE users ALTER COLUMN email SET NOT NULL")
    cur.execute("ALTER TABLE users ALTER COLUMN role SET NOT NULL")
    cur.execute("ALTER TABLE users ALTER COLUMN team SET NOT NULL")
    cur.execute("ALTER TABLE users ALTER COLUMN description SET NOT NULL")
    cur.execute("ALTER TABLE users ALTER COLUMN is_active SET NOT NULL")
    cur.execute("ALTER TABLE users ALTER COLUMN created_at SET NOT NULL")


def init_db() -> None:
    logger.info("Initializing database schema")
    with get_connection() as conn:
        with conn.cursor() as cur:
            ensure_user_schema(cur)

            cur.execute("SELECT COUNT(*) AS total FROM users")
            count_row = cur.fetchone()
            count = count_row["total"] if count_row else 0

            if count == 0:
                logger.info("Seeding initial users")
                cur.execute(
                    """
                    INSERT INTO users (
                        name,
                        email,
                        role,
                        team,
                        description,
                        is_active,
                        created_at
                    )
                    VALUES
                        (
                            'Alice Johnson',
                            'alice.johnson@example.com',
                            'Platform Engineer',
                            'Platform',
                            'Builds internal deployment tooling and improves application reliability in production.',
                            TRUE,
                            NOW()
                        ),
                        (
                            'Bob Martin',
                            'bob.martin@example.com',
                            'Site Reliability Engineer',
                            'Operations',
                            'Maintains observability, incident response workflows, and runtime stability.',
                            TRUE,
                            NOW()
                        ),
                        (
                            'Charlie Dupont',
                            'charlie.dupont@example.com',
                            'DevOps Manager',
                            'Engineering',
                            'Coordinates platform delivery, production standards, and cross-team infrastructure priorities.',
                            TRUE,
                            NOW()
                        )
                    """
                )

        conn.commit()


@app.on_event("startup")
def startup_event() -> None:
    logger.info(
        "Starting application in %s mode with database host %s:%s",
        settings.app_env,
        settings.db_host,
        settings.db_port,
    )

    for attempt in range(1, settings.db_init_retries + 1):
        try:
            logger.info(
                "Attempt %s/%s to initialize database",
                attempt,
                settings.db_init_retries,
            )
            init_db()
            logger.info("Database initialized successfully")
            return
        except Exception:
            logger.exception(
                "Database initialization failed on attempt %s/%s",
                attempt,
                settings.db_init_retries,
            )
            time.sleep(settings.db_init_retry_delay_seconds)

    raise RuntimeError("Could not initialize database after multiple attempts")


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=str(exc.detail)).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(detail=str(exc)).model_dump(),
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled server error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(detail="Internal server error").model_dump(),
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started_at = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - started_at) * 1000
    logger.info(
        "%s %s -> %s in %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/health", response_model=HealthResponse, tags=["monitoring"])
def health() -> HealthResponse:
    database_status = "ok" if check_database() else "unavailable"
    service_status = "ok" if database_status == "ok" else "degraded"
    return HealthResponse(
        status=service_status,
        version=settings.app_version,
        environment=settings.app_env,
        database=database_status,
        timestamp=datetime.now(UTC),
    )


@app.get("/users", response_model=UsersResponse, tags=["users"])
def get_users() -> UsersResponse:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT
                id,
                name,
                email,
                role,
                team,
                description,
                is_active,
                created_at
            FROM users
            ORDER BY id
            """
        )
        rows = cur.fetchall()

    users = [User.model_validate(row) for row in rows]
    return UsersResponse(users=users, total=len(users))


@app.get("/users/{user_id}", response_model=User, tags=["users"])
def get_user(user_id: int) -> User:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT
                id,
                name,
                email,
                role,
                team,
                description,
                is_active,
                created_at
            FROM users
            WHERE id = %s
            """,
            (user_id,),
        )
        row = cur.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )

    return User.model_validate(row)


@app.get("/version", response_model=VersionResponse, tags=["monitoring"])
def version() -> VersionResponse:
    return VersionResponse(
        version=settings.app_version,
        environment=settings.app_env,
    )
