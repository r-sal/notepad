from datetime import datetime, timedelta
from uuid import UUID

from httpx import AsyncClient
from sqlalchemy import select, update

from app.core.database import async_session
from app.core.scheduler import TRASH_RETENTION_DAYS, purge_expired_trash
from app.models.note import Note
from tests.helpers import auth_header, create_note, create_user


async def _age_trashed_note(note_id: str, days_ago: int):
    """Set trashed_at to N days ago directly in the database."""
    aged_time = datetime.utcnow() - timedelta(days=days_ago)
    async with async_session() as db:
        await db.execute(
            update(Note)
            .where(Note.id == UUID(note_id))
            .values(trashed_at=aged_time)
        )
        await db.commit()


class TestTrashCleanup:
    async def test_purge_deletes_expired_notes(self, client: AsyncClient):
        """Notes trashed more than 30 days ago should be permanently deleted."""
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens, title="Old Trash")
            # Soft delete the note
            await client.delete(f"/api/notes/{note['id']}", headers=auth_header(tokens))
            # Age it beyond retention period
            await _age_trashed_note(note["id"], days_ago=31)

            count = await purge_expired_trash()
            assert count == 1

            # Verify note is gone
            res = await client.get(
                f"/api/notes/{note['id']}", headers=auth_header(tokens)
            )
            assert res.status_code == 404

    async def test_purge_keeps_recent_trash(self, client: AsyncClient):
        """Notes trashed less than 30 days ago should be kept."""
        async with client:
            _, _, tokens = await create_user(client)
            note = await create_note(client, tokens, title="Recent Trash")
            await client.delete(f"/api/notes/{note['id']}", headers=auth_header(tokens))
            # Age it to 10 days (within retention)
            await _age_trashed_note(note["id"], days_ago=10)

            count = await purge_expired_trash()
            assert count == 0

            # Verify note still exists
            res = await client.get(
                f"/api/notes/{note['id']}", headers=auth_header(tokens)
            )
            assert res.status_code == 200
            assert res.json()["is_trashed"] is True

    async def test_purge_ignores_non_trashed_notes(self, client: AsyncClient):
        """Active notes should never be deleted by the cleanup job."""
        async with client:
            _, _, tokens = await create_user(client)
            await create_note(client, tokens, title="Active Note")

            count = await purge_expired_trash()
            assert count == 0

    async def test_purge_mixed_ages(self, client: AsyncClient):
        """Only expired notes should be purged when mixed ages exist."""
        async with client:
            _, _, tokens = await create_user(client)

            old_note = await create_note(client, tokens, title="Old Note")
            await client.delete(f"/api/notes/{old_note['id']}", headers=auth_header(tokens))
            await _age_trashed_note(old_note["id"], days_ago=45)

            recent_note = await create_note(client, tokens, title="Recent Note")
            await client.delete(f"/api/notes/{recent_note['id']}", headers=auth_header(tokens))
            await _age_trashed_note(recent_note["id"], days_ago=5)

            count = await purge_expired_trash()
            assert count == 1

            # Old note is gone
            res_old = await client.get(
                f"/api/notes/{old_note['id']}", headers=auth_header(tokens)
            )
            assert res_old.status_code == 404

            # Recent note still exists
            res_recent = await client.get(
                f"/api/notes/{recent_note['id']}", headers=auth_header(tokens)
            )
            assert res_recent.status_code == 200

    async def test_purge_no_trash_returns_zero(self, client: AsyncClient):
        """Running cleanup with no trashed notes returns zero."""
        async with client:
            count = await purge_expired_trash()
            assert count == 0

    async def test_retention_days_constant(self):
        """Verify the retention period is 30 days."""
        assert TRASH_RETENTION_DAYS == 30
