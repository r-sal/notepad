import os

# Must be set before importing app modules so the engine uses NullPool
os.environ["TESTING"] = "1"

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def client():
    """Returns a fresh async client for each test."""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")
