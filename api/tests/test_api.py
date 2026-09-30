import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure test env before app imports mutate settings cache
os.environ["SECRET_KEY"] = "test-secret"
os.environ["BOT_API_TOKEN"] = "test-bot-token"
os.environ["DATABASE_URL"] = "sqlite://"

from app.config import get_settings
from app.database import Base, get_db
from app.main import app

get_settings.cache_clear()

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_register_login_create_expense(client: TestClient):
    r = client.post("/api/auth/register", json={"email": "a@example.com", "password": "password123"})
    assert r.status_code == 201
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post(
        "/api/expenses",
        headers=headers,
        json={"amount": "12.50", "category": "food", "note": "cafe"},
    )
    assert r.status_code == 201
    assert r.json()["amount"] == "12.50"

    r = client.get("/api/expenses/summary/month", headers=headers)
    assert r.status_code == 200
    assert float(r.json()["total"]) == 12.5


def test_bot_flow(client: TestClient):
    r = client.post("/api/auth/register", json={"email": "b@example.com", "password": "password123"})
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    code = client.post("/api/link-codes", headers=headers).json()["code"]

    bot_headers = {"Authorization": "Bearer test-bot-token"}
    r = client.post("/api/bot/link", headers=bot_headers, json={"telegram_id": "99", "code": code})
    assert r.status_code == 200

    r = client.post(
        "/api/bot/expenses",
        headers=bot_headers,
        json={"telegram_id": "99", "amount": "3.20", "note": "metro", "category": "transport"},
    )
    assert r.status_code == 201
