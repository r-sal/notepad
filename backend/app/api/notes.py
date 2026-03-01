from uuid import UUID

import bleach
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteListResponse, NoteResponse, NoteUpdate

router = APIRouter(prefix="/api/notes", tags=["notes"])

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "s", "u",
    "h1", "h2", "h3",
    "ul", "ol", "li",
    "blockquote", "pre", "code",
    "a", "hr",
]
ALLOWED_ATTRS = {"a": ["href", "title", "target"]}


def sanitize_body(body: str) -> str:
    return bleach.clean(body, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)


@router.get("", response_model=list[NoteListResponse])
async def list_notes(
    folder_id: str | None = Query(None),
    starred: bool | None = Query(None),
    trashed: bool | None = Query(None),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Note).where(Note.user_id == current_user.id)

    if trashed is True:
        query = query.where(Note.is_trashed == True)
    else:
        # By default, exclude trashed notes
        query = query.where(Note.is_trashed == False)

    if folder_id is not None:
        query = query.where(Note.folder_id == UUID(folder_id))

    if starred is True:
        query = query.where(Note.is_starred == True)

    if search:
        query = query.where(
            Note.search_vector.op("@@")(func.plainto_tsquery("english", search))
        )

    query = query.order_by(Note.updated_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    body: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = Note(
        title=body.title,
        body=sanitize_body(body.body),
        folder_id=UUID(body.folder_id) if body.folder_id else None,
        user_id=current_user.id,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Note).where(Note.id == UUID(note_id), Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    body: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Note).where(Note.id == UUID(note_id), Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if body.title is not None:
        note.title = body.title
    if body.body is not None:
        note.body = sanitize_body(body.body)
    if body.folder_id is not None:
        note.folder_id = UUID(body.folder_id) if body.folder_id else None
    if body.is_starred is not None:
        note.is_starred = body.is_starred

    note.updated_at = func.now()
    await db.commit()
    await db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_200_OK)
async def soft_delete_note(
    note_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Note).where(Note.id == UUID(note_id), Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    note.is_trashed = True
    note.trashed_at = func.now()
    await db.commit()
    return {"detail": "Note moved to trash"}


@router.post("/{note_id}/restore", response_model=NoteResponse)
async def restore_note(
    note_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Note).where(
            Note.id == UUID(note_id),
            Note.user_id == current_user.id,
            Note.is_trashed == True,
        )
    )
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found in trash")

    note.is_trashed = False
    note.trashed_at = None
    await db.commit()
    await db.refresh(note)
    return note


@router.delete("/{note_id}/permanent", status_code=status.HTTP_200_OK)
async def permanent_delete_note(
    note_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Note).where(
            Note.id == UUID(note_id),
            Note.user_id == current_user.id,
            Note.is_trashed == True,
        )
    )
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found in trash")

    await db.delete(note)
    await db.commit()
    return {"detail": "Note permanently deleted"}
