from httpx import AsyncClient

from tests.helpers import auth_header, create_folder, create_note, create_user


class TestCreateFolder:
    async def test_create_folder(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            res = await client.post("/api/folders", json={
                "name": "My Folder",
            }, headers=auth_header(tokens))
            assert res.status_code == 201
            data = res.json()
            assert data["name"] == "My Folder"
            assert data["parent_id"] is None
            assert data["sort_order"] == 0

    async def test_create_nested_folder(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            parent = await create_folder(client, tokens, name="Parent")
            res = await client.post("/api/folders", json={
                "name": "Child",
                "parent_id": parent["id"],
            }, headers=auth_header(tokens))
            assert res.status_code == 201
            data = res.json()
            assert data["name"] == "Child"
            assert data["parent_id"] == parent["id"]

    async def test_create_folder_invalid_parent(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            res = await client.post("/api/folders", json={
                "name": "Orphan",
                "parent_id": "00000000-0000-0000-0000-000000000000",
            }, headers=auth_header(tokens))
            assert res.status_code == 404

    async def test_create_folder_requires_auth(self, client: AsyncClient):
        async with client:
            res = await client.post("/api/folders", json={"name": "Test"})
            assert res.status_code == 403

    async def test_create_folder_other_users_parent(self, client: AsyncClient):
        """Cannot create a child folder under another user's folder."""
        async with client:
            _, _, tokens1 = await create_user(client)
            _, _, tokens2 = await create_user(client)
            parent = await create_folder(client, tokens1, name="User1 Folder")
            res = await client.post("/api/folders", json={
                "name": "Sneaky Child",
                "parent_id": parent["id"],
            }, headers=auth_header(tokens2))
            assert res.status_code == 404


class TestListFolders:
    async def test_list_folders_empty(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            res = await client.get("/api/folders", headers=auth_header(tokens))
            assert res.status_code == 200
            assert res.json() == []

    async def test_list_folders_flat(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            await create_folder(client, tokens, name="Folder A")
            await create_folder(client, tokens, name="Folder B")
            res = await client.get("/api/folders", headers=auth_header(tokens))
            assert res.status_code == 200
            data = res.json()
            assert len(data) == 2
            names = [f["name"] for f in data]
            assert "Folder A" in names
            assert "Folder B" in names

    async def test_list_folders_tree_structure(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            parent = await create_folder(client, tokens, name="Parent")
            await create_folder(client, tokens, name="Child 1", parent_id=parent["id"])
            await create_folder(client, tokens, name="Child 2", parent_id=parent["id"])
            res = await client.get("/api/folders", headers=auth_header(tokens))
            assert res.status_code == 200
            data = res.json()
            # Should have 1 root folder with 2 children
            assert len(data) == 1
            assert data[0]["name"] == "Parent"
            assert len(data[0]["children"]) == 2
            child_names = [c["name"] for c in data[0]["children"]]
            assert "Child 1" in child_names
            assert "Child 2" in child_names

    async def test_list_folders_deep_nesting(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            level1 = await create_folder(client, tokens, name="Level 1")
            level2 = await create_folder(client, tokens, name="Level 2", parent_id=level1["id"])
            level3 = await create_folder(client, tokens, name="Level 3", parent_id=level2["id"])
            res = await client.get("/api/folders", headers=auth_header(tokens))
            assert res.status_code == 200
            data = res.json()
            assert len(data) == 1
            assert data[0]["name"] == "Level 1"
            assert len(data[0]["children"]) == 1
            assert data[0]["children"][0]["name"] == "Level 2"
            assert len(data[0]["children"][0]["children"]) == 1
            assert data[0]["children"][0]["children"][0]["name"] == "Level 3"

    async def test_list_folders_isolates_users(self, client: AsyncClient):
        async with client:
            _, _, tokens1 = await create_user(client)
            _, _, tokens2 = await create_user(client)
            await create_folder(client, tokens1, name="User1 Folder")
            await create_folder(client, tokens2, name="User2 Folder")
            res = await client.get("/api/folders", headers=auth_header(tokens1))
            assert res.status_code == 200
            data = res.json()
            assert len(data) == 1
            assert data[0]["name"] == "User1 Folder"


class TestUpdateFolder:
    async def test_rename_folder(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            folder = await create_folder(client, tokens, name="Old Name")
            res = await client.put(
                f"/api/folders/{folder['id']}",
                json={"name": "New Name"},
                headers=auth_header(tokens),
            )
            assert res.status_code == 200
            assert res.json()["name"] == "New Name"

    async def test_move_folder_to_new_parent(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            parent = await create_folder(client, tokens, name="New Parent")
            child = await create_folder(client, tokens, name="Moving Folder")
            res = await client.put(
                f"/api/folders/{child['id']}",
                json={"parent_id": parent["id"]},
                headers=auth_header(tokens),
            )
            assert res.status_code == 200
            assert res.json()["parent_id"] == parent["id"]

    async def test_move_folder_to_root(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            parent = await create_folder(client, tokens, name="Parent")
            child = await create_folder(client, tokens, name="Child", parent_id=parent["id"])
            # Move to root by setting parent_id to empty string
            res = await client.put(
                f"/api/folders/{child['id']}",
                json={"parent_id": ""},
                headers=auth_header(tokens),
            )
            assert res.status_code == 200
            assert res.json()["parent_id"] is None

    async def test_cannot_move_folder_into_itself(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            folder = await create_folder(client, tokens, name="Self Ref")
            res = await client.put(
                f"/api/folders/{folder['id']}",
                json={"parent_id": folder["id"]},
                headers=auth_header(tokens),
            )
            assert res.status_code == 400

    async def test_update_sort_order(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            folder = await create_folder(client, tokens, name="Reorder Me")
            res = await client.put(
                f"/api/folders/{folder['id']}",
                json={"sort_order": 5},
                headers=auth_header(tokens),
            )
            assert res.status_code == 200
            assert res.json()["sort_order"] == 5

    async def test_update_folder_not_found(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            res = await client.put(
                "/api/folders/00000000-0000-0000-0000-000000000000",
                json={"name": "Ghost"},
                headers=auth_header(tokens),
            )
            assert res.status_code == 404


class TestDeleteFolder:
    async def test_delete_empty_folder(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            folder = await create_folder(client, tokens, name="Empty")
            res = await client.delete(
                f"/api/folders/{folder['id']}", headers=auth_header(tokens)
            )
            assert res.status_code == 200
            # Verify it's gone
            list_res = await client.get("/api/folders", headers=auth_header(tokens))
            assert len(list_res.json()) == 0

    async def test_delete_folder_trashes_notes(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            folder = await create_folder(client, tokens, name="Has Notes")
            await create_note(client, tokens, title="Note In Folder", folder_id=folder["id"])
            res = await client.delete(
                f"/api/folders/{folder['id']}", headers=auth_header(tokens)
            )
            assert res.status_code == 200
            assert res.json()["notes_trashed"] == 1
            # Verify note is trashed
            notes_res = await client.get(
                "/api/notes?trashed=true", headers=auth_header(tokens)
            )
            assert len(notes_res.json()) == 1
            assert notes_res.json()[0]["title"] == "Note In Folder"

    async def test_delete_folder_cascades_to_children(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            parent = await create_folder(client, tokens, name="Parent")
            child = await create_folder(client, tokens, name="Child", parent_id=parent["id"])
            await create_note(client, tokens, title="Child Note", folder_id=child["id"])
            res = await client.delete(
                f"/api/folders/{parent['id']}", headers=auth_header(tokens)
            )
            assert res.status_code == 200
            # Both parent and child folders gone
            list_res = await client.get("/api/folders", headers=auth_header(tokens))
            assert len(list_res.json()) == 0
            # Note in child folder is trashed
            notes_res = await client.get(
                "/api/notes?trashed=true", headers=auth_header(tokens)
            )
            assert len(notes_res.json()) == 1
            assert notes_res.json()[0]["title"] == "Child Note"

    async def test_delete_folder_not_found(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            res = await client.delete(
                "/api/folders/00000000-0000-0000-0000-000000000000",
                headers=auth_header(tokens),
            )
            assert res.status_code == 404

    async def test_delete_folder_wrong_user(self, client: AsyncClient):
        async with client:
            _, _, tokens1 = await create_user(client)
            _, _, tokens2 = await create_user(client)
            folder = await create_folder(client, tokens1, name="Private")
            res = await client.delete(
                f"/api/folders/{folder['id']}", headers=auth_header(tokens2)
            )
            assert res.status_code == 404


class TestNotesInFolders:
    async def test_list_notes_by_folder(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            folder = await create_folder(client, tokens, name="Work")
            await create_note(client, tokens, title="Work Note", folder_id=folder["id"])
            await create_note(client, tokens, title="Personal Note")
            res = await client.get(
                f"/api/notes?folder_id={folder['id']}", headers=auth_header(tokens)
            )
            assert res.status_code == 200
            assert len(res.json()) == 1
            assert res.json()[0]["title"] == "Work Note"

    async def test_move_note_to_folder(self, client: AsyncClient):
        async with client:
            _, _, tokens = await create_user(client)
            folder = await create_folder(client, tokens, name="Destination")
            note = await create_note(client, tokens, title="Movable Note")
            res = await client.put(
                f"/api/notes/{note['id']}",
                json={"folder_id": folder["id"]},
                headers=auth_header(tokens),
            )
            assert res.status_code == 200
            assert res.json()["folder_id"] == folder["id"]
