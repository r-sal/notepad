import logging
from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.note import Note

logger = logging.getLogger(__name__)

TRASH_RETENTION_DAYS = 30


async def purge_expired_trash():
    """Permanently delete notes that have been in the trash longer than TRASH_RETENTION_DAYS."""
    cutoff = datetime.utcnow() - timedelta(days=TRASH_RETENTION_DAYS)

    async with async_session() as db:
        result = await db.execute(
            select(Note).where(
                Note.is_trashed == True,
                Note.trashed_at != None,
                Note.trashed_at < cutoff,
            )
        )
        expired_notes = result.scalars().all()
        count = len(expired_notes)

        if count > 0:
            for note in expired_notes:
                await db.delete(note)
            await db.commit()
            logger.info(f"Purged {count} expired notes from trash")
        else:
            logger.debug("No expired trash to purge")

    return count
