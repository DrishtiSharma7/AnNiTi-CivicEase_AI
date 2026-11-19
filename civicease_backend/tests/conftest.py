import os
import tempfile

# Must be set before the app is imported.
os.environ.update({
    "APP_ENV": "test", "DATABASE_URL": "sqlite://", "USE_MOCK_LLM": "true", "JUDGE_MODE": "true",
    "STORAGE_DIR": tempfile.mkdtemp(), "ALLOWED_PORTAL_DOMAINS": "localhost,127.0.0.1,testserver",
    "RATE_LIMIT_PER_MINUTE": "10000", "AUTH_RATE_LIMIT_PER_MINUTE": "10000",
    "REVIEWER_EMAILS": "reviewer@example.com,second@example.com", "METRICS_TOKEN": "test-metrics", "ALLOW_SELF_APPROVE": "false",
})

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth(client):
    email = f"user{os.urandom(4).hex()}@example.com"
    r = client.post("/auth/register", json={"email": email, "password": "correct-horse-battery"})
    token = r.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def reviewer(client):
    r = client.post("/auth/register", json={"email": "reviewer@example.com", "password": "correct-horse-battery"})
    if r.status_code == 409:
        r = client.post("/auth/login", json={"email": "reviewer@example.com", "password": "correct-horse-battery"})
    return {"Authorization": f"Bearer {r.json()['data']['access_token']}"}
