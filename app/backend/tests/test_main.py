import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import main


client = TestClient(main.app)


def test_version_returns_application_metadata():
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {
        "version": main.settings.app_version,
        "environment": main.settings.app_env,
    }


def test_health_reports_ok_when_database_is_available(monkeypatch):
    monkeypatch.setattr(main, "check_database", lambda: True)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["version"] == main.settings.app_version
    assert body["environment"] == main.settings.app_env
    assert "timestamp" in body


def test_health_reports_degraded_when_database_is_unavailable(monkeypatch):
    monkeypatch.setattr(main, "check_database", lambda: False)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["database"] == "unavailable"
