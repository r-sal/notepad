from httpx import AsyncClient

from tests.helpers import auth_header, create_note, create_user


class TestCreateNote:
    async def test_create_note(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            res = await client.post("/api/notes", json={
                "title": "My Note",
                "body": "Hello world",
            }, headers=auth_header(tokens))
            assert res.status_code == 201
            data = res.json()
            assert data["title"] == "My Note"
            assert data["body"] == "Hello world"
            assert data["is_starred"] is False
            assert data["is_trashed"] is False
            assert data["folder_id"] is None

    async def test_create_note_defaults(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            res = await client.post("/api/notes", json={}, headers=auth_header(tokens))
            assert res.status_code == 201
            data = res.json()
            assert data["title"] == "Untitled"
            assert data["body"] == ""

    async def test_create_note_requires_auth(self, client: AsyncClient):
        async with client:
            res = await client.post("/api/notes", json={"title": "Test"})
            assert res.status_code == 403


class TestGetNote:
    async def test_get_note(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens)
            res = await client.get(f"/api/notes/{note['id']}", headers=auth_header(tokens))
            assert res.status_code == 200
            assert res.json()["id"] == note["id"]

    async def test_get_note_not_found(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            res = await client.get(
                "/api/notes/00000000-0000-0000-0000-000000000000",
                headers=auth_header(tokens),
            )
            assert res.status_code == 404

    async def test_get_note_wrong_user(self, client: AsyncClient):
        async with client:
            _, _, tokens1 = await create_user(client)
            _, _, tokens2 = await create_user(client)
            note = await create_note(client, tokens1)
            res = await client.get(f"/api/notes/{note['id']}", headers=auth_header(tokens2))
            assert res.status_code == 404


class TestUpdateNote:
    async def test_update_title(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens)
            res = await client.put(
                f"/api/notes/{note['id']}",
                json={"title": "Updated Title"},
                headers=auth_header(tokens),
            )
            assert res.status_code == 200
            assert res.json()["title"] == "Updated Title"
            assert res.json()["body"] == note["body"]  # unchanged

    async def test_update_body(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens)
            res = await client.put(
                f"/api/notes/{note['id']}",
                json={"body": "New body content"},
                headers=auth_header(tokens),
            )
            assert res.status_code == 200
            assert res.json()["body"] == "New body content"

    async def test_star_note(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens)
            res = await client.put(
                f"/api/notes/{note['id']}",
                json={"is_starred": True},
                headers=auth_header(tokens),
            )
            assert res.status_code == 200
            assert res.json()["is_starred"] is True


class TestListNotes:
    async def test_list_notes(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            await create_note(client, tokens, title="Note 1")
            await create_note(client, tokens, title="Note 2")
            res = await client.get("/api/notes", headers=auth_header(tokens))
            assert res.status_code == 200
            data = res.json()
            assert len(data) == 2

    async def test_list_excludes_trashed(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens, title="Trashed Note")
            await create_note(client, tokens, title="Active Note")
            await client.delete(f"/api/notes/{note['id']}", headers=auth_header(tokens))
            res = await client.get("/api/notes", headers=auth_header(tokens))
            assert res.status_code == 200
            titles = [n["title"] for n in res.json()]
            assert "Active Note" in titles
            assert "Trashed Note" not in titles

    async def test_list_trashed_notes(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens, title="Trashed Note")
            await client.delete(f"/api/notes/{note['id']}", headers=auth_header(tokens))
            res = await client.get("/api/notes?trashed=true", headers=auth_header(tokens))
            assert res.status_code == 200
            assert len(res.json()) == 1
            assert res.json()[0]["title"] == "Trashed Note"

    async def test_list_starred_notes(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens, title="Starred")
            await create_note(client, tokens, title="Normal")
            await client.put(
                f"/api/notes/{note['id']}",
                json={"is_starred": True},
                headers=auth_header(tokens),
            )
            res = await client.get("/api/notes?starred=true", headers=auth_header(tokens))
            assert res.status_code == 200
            assert len(res.json()) == 1
            assert res.json()[0]["title"] == "Starred"

    async def test_list_isolates_users(self, client: AsyncClient):
        async with client:
            _, _, tokens1 = await create_user(client)
            _, _, tokens2 = await create_user(client)
            await create_note(client, tokens1, title="User1 Note")
            await create_note(client, tokens2, title="User2 Note")
            res = await client.get("/api/notes", headers=auth_header(tokens1))
            assert len(res.json()) == 1
            assert res.json()[0]["title"] == "User1 Note"


class TestSoftDelete:
    async def test_soft_delete(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens)
            res = await client.delete(f"/api/notes/{note['id']}", headers=auth_header(tokens))
            assert res.status_code == 200
            # Verify it's trashed
            get_res = await client.get(f"/api/notes/{note['id']}", headers=auth_header(tokens))
            assert get_res.json()["is_trashed"] is True
            assert get_res.json()["trashed_at"] is not None


class TestRestore:
    async def test_restore_note(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens)
            await client.delete(f"/api/notes/{note['id']}", headers=auth_header(tokens))
            res = await client.post(
                f"/api/notes/{note['id']}/restore", headers=auth_header(tokens)
            )
            assert res.status_code == 200
            assert res.json()["is_trashed"] is False
            assert res.json()["trashed_at"] is None

    async def test_restore_non_trashed_fails(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens)
            res = await client.post(
                f"/api/notes/{note['id']}/restore", headers=auth_header(tokens)
            )
            assert res.status_code == 404


class TestPermanentDelete:
    async def test_permanent_delete(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens)
            await client.delete(f"/api/notes/{note['id']}", headers=auth_header(tokens))
            res = await client.delete(
                f"/api/notes/{note['id']}/permanent", headers=auth_header(tokens)
            )
            assert res.status_code == 200
            # Verify it's gone
            get_res = await client.get(f"/api/notes/{note['id']}", headers=auth_header(tokens))
            assert get_res.status_code == 404

    async def test_permanent_delete_non_trashed_fails(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens)
            res = await client.delete(
                f"/api/notes/{note['id']}/permanent", headers=auth_header(tokens)
            )
            assert res.status_code == 404


class TestSearch:
    async def test_search_by_title(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            await create_note(client, tokens, title="Python Tutorial", body="Learn Python")
            await create_note(client, tokens, title="Grocery List", body="Buy milk")
            res = await client.get("/api/notes?search=python", headers=auth_header(tokens))
            assert res.status_code == 200
            assert len(res.json()) == 1
            assert res.json()[0]["title"] == "Python Tutorial"

    async def test_search_by_body(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            await create_note(client, tokens, title="Note A", body="contains unique keyword zephyr")
            await create_note(client, tokens, title="Note B", body="nothing special")
            res = await client.get("/api/notes?search=zephyr", headers=auth_header(tokens))
            assert res.status_code == 200
            assert len(res.json()) == 1
            assert res.json()[0]["title"] == "Note A"


class TestSanitization:
    async def test_xss_in_body_is_stripped(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            res = await client.post("/api/notes", json={
                "title": "XSS Test",
                "body": '<p>Hello</p><script>alert("xss")</script>',
            }, headers=auth_header(tokens))
            assert res.status_code == 201
            assert "<script>" not in res.json()["body"]
            assert "<p>Hello</p>" in res.json()["body"]


class TestTemporaryNotes:
    async def test_create_temporary_note(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens, title="Scratch", is_temporary=True)
            assert note["is_temporary"] is True

    async def test_default_create_not_temporary(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens, title="Regular")
            assert note["is_temporary"] is False

    async def test_list_excludes_temporary_by_default(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            await create_note(client, tokens, title="Regular Note")
            await create_note(client, tokens, title="Temp Note", is_temporary=True)
            res = await client.get("/api/notes", headers=auth_header(tokens))
            assert res.status_code == 200
            titles = [n["title"] for n in res.json()]
            assert "Regular Note" in titles
            assert "Temp Note" not in titles

    async def test_list_temporary_only(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            await create_note(client, tokens, title="Regular Note")
            await create_note(client, tokens, title="Temp Note", is_temporary=True)
            res = await client.get("/api/notes?temporary=true", headers=auth_header(tokens))
            assert res.status_code == 200
            titles = [n["title"] for n in res.json()]
            assert "Regular Note" not in titles
            assert "Temp Note" in titles

    async def test_search_finds_temporary_notes(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            await create_note(client, tokens, title="Unique Scratchpad Item", body="findable text", is_temporary=True)
            res = await client.get("/api/notes?search=scratchpad", headers=auth_header(tokens))
            assert res.status_code == 200
            titles = [n["title"] for n in res.json()]
            assert "Unique Scratchpad Item" in titles

    async def test_starred_includes_temporary(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens, title="Starred Temp", is_temporary=True)
            # Star the temporary note
            await client.put(
                f"/api/notes/{note['id']}",
                json={"is_starred": True},
                headers=auth_header(tokens),
            )
            res = await client.get("/api/notes?starred=true", headers=auth_header(tokens))
            assert res.status_code == 200
            titles = [n["title"] for n in res.json()]
            assert "Starred Temp" in titles

    async def test_promote_note(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens, title="Promote Me", is_temporary=True)
            res = await client.post(
                f"/api/notes/{note['id']}/promote",
                headers=auth_header(tokens),
            )
            assert res.status_code == 200
            assert res.json()["is_temporary"] is False
            # Now it should appear in All Notes
            res = await client.get("/api/notes", headers=auth_header(tokens))
            titles = [n["title"] for n in res.json()]
            assert "Promote Me" in titles

    async def test_promote_non_temporary_returns_404(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens, title="Regular")
            res = await client.post(
                f"/api/notes/{note['id']}/promote",
                headers=auth_header(tokens),
            )
            assert res.status_code == 404

    async def test_promote_via_update(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens, title="Via Update", is_temporary=True)
            res = await client.put(
                f"/api/notes/{note['id']}",
                json={"is_temporary": False},
                headers=auth_header(tokens),
            )
            assert res.status_code == 200
            assert res.json()["is_temporary"] is False

    async def test_temporary_note_can_be_trashed(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens, title="Trash Temp", is_temporary=True)
            res = await client.delete(
                f"/api/notes/{note['id']}",
                headers=auth_header(tokens),
            )
            assert res.status_code == 200
            # Should appear in trash
            res = await client.get("/api/notes?trashed=true", headers=auth_header(tokens))
            titles = [n["title"] for n in res.json()]
            assert "Trash Temp" in titles

    async def test_promote_other_users_note_returns_404(self, client: AsyncClient):
        async with client:
            _, _, tokens_a = await create_user(client)
            _, _, tokens_b = await create_user(client)
            note = await create_note(client, tokens_a, title="A's Temp", is_temporary=True)
            res = await client.post(
                f"/api/notes/{note['id']}/promote",
                headers=auth_header(tokens_b),
            )
            assert res.status_code == 404
