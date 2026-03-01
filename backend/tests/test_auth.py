from uuid import uuid4

from httpx import AsyncClient

from tests.helpers import create_user


class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        async with client:
            res = await client.post("/api/auth/register", json={
                "email": f"register_{uuid4().hex[:8]}@test.com",
                "password": "securepass123",
            })
            assert res.status_code == 201
            data = res.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"

    async def test_register_duplicate_email(self, client: AsyncClient):
        async with client:
            email, _, _ = await create_user(client)
            res = await client.post("/api/auth/register", json={
                "email": email,
                "password": "anything",
            })
            assert res.status_code == 409
            assert res.json()["detail"] == "Email already registered"

    async def test_register_invalid_email(self, client: AsyncClient):
        async with client:
            res = await client.post("/api/auth/register", json={
                "email": "not-an-email",
                "password": "securepass123",
            })
            assert res.status_code == 422


class TestLogin:
    async def test_login_success(self, client: AsyncClient):
        async with client:
            email, password, _ = await create_user(client)
            res = await client.post("/api/auth/login", json={
                "email": email,
                "password": password,
            })
            assert res.status_code == 200
            data = res.json()
            assert "access_token" in data
            assert "refresh_token" in data

    async def test_login_wrong_password(self, client: AsyncClient):
        async with client:
            email, _, _ = await create_user(client)
            res = await client.post("/api/auth/login", json={
                "email": email,
                "password": "wrongpassword",
            })
            assert res.status_code == 401
            assert res.json()["detail"] == "Invalid email or password"

    async def test_login_nonexistent_user(self, client: AsyncClient):
        async with client:
            res = await client.post("/api/auth/login", json={
                "email": "nobody@test.com",
                "password": "anything",
            })
            assert res.status_code == 401


class TestRefresh:
    async def test_refresh_success(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            res = await client.post("/api/auth/refresh", json={
                "refresh_token": tokens["refresh_token"],
            })
            assert res.status_code == 200
            data = res.json()
            assert "access_token" in data
            assert "refresh_token" in data

    async def test_refresh_with_invalid_token(self, client: AsyncClient):
        async with client:
            res = await client.post("/api/auth/refresh", json={
                "refresh_token": "invalid.token.here",
            })
            assert res.status_code == 401

    async def test_refresh_with_access_token_rejected(self, client: AsyncClient):
        """Access tokens should not be accepted as refresh tokens."""
        async with client:
            _, _, tokens = await create_user(client)
            res = await client.post("/api/auth/refresh", json={
                "refresh_token": tokens["access_token"],
            })
            assert res.status_code == 401


class TestLogout:
    async def test_logout(self, client: AsyncClient):
        async with client:
            res = await client.post("/api/auth/logout")
            assert res.status_code == 200


class TestProtectedRoutes:
    async def test_health_is_public(self, client: AsyncClient):
        async with client:
            res = await client.get("/api/health")
            assert res.status_code == 200
            assert res.json() == {"status": "ok"}
