from uuid import uuid4

from httpx import AsyncClient


async def create_user(client: AsyncClient, email: str | None = None, password: str = "testpassword123"):
    """Register a user and return (email, password, tokens)."""
    if email is None:
        email = f"user_{uuid4().hex[:8]}@test.com"
    res = await client.post("/api/auth/register", json={
        "email": email,
        "password": password,
    })
    assert res.status_code == 201
    return email, password, res.json()


def auth_header(tokens: dict) -> dict:
    """Build Authorization header from tokens dict."""
    return {"Authorization": f"Bearer {tokens['access_token']}"}


async def create_note(
    client: AsyncClient,
    tokens: dict,
    title: str = "Test Note",
    body: str = "Test body content",
    folder_id: str | None = None,
    is_temporary: bool = False,
) -> dict:
    """Create a note and return the response data."""
    payload: dict = {"title": title, "body": body, "is_temporary": is_temporary}
    if folder_id:
        payload["folder_id"] = folder_id
    res = await client.post("/api/notes", json=payload, headers=auth_header(tokens))
    assert res.status_code == 201
    return res.json()


async def create_folder(
    client: AsyncClient,
    tokens: dict,
    name: str = "Test Folder",
    parent_id: str | None = None,
) -> dict:
    """Create a folder and return the response data."""
    payload = {"name": name}
    if parent_id:
        payload["parent_id"] = parent_id
    res = await client.post("/api/folders", json=payload, headers=auth_header(tokens))
    assert res.status_code == 201
    return res.json()
