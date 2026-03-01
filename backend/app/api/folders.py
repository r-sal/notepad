from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.folder import Folder
from app.models.note import Note
from app.models.user import User
from app.schemas.folder import (
    FolderCreate,
    FolderResponse,
    FolderTreeResponse,
    FolderUpdate,
)

router = APIRouter(prefix="/api/folders", tags=["folders"])


def build_tree(folders: list[Folder], parent_id: UUID | None = None) -> list[dict]:
    """Recursively build a nested tree from a flat list of folders."""
    tree = []
    for folder in folders:
        if folder.parent_id == parent_id:
            node = {
                "id": folder.id,
                "name": folder.name,
                "parent_id": folder.parent_id,
                "sort_order": folder.sort_order,
                "created_at": folder.created_at,
                "updated_at": folder.updated_at,
                "children": build_tree(folders, folder.id),
            }
            tree.append(node)
    tree.sort(key=lambda f: f["sort_order"])
    return tree


@router.get("", response_model=list[FolderTreeResponse])
async def list_folders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all folders as a nested tree structure."""
    result = await db.execute(
        select(Folder)
        .where(Folder.user_id == current_user.id)
        .order_by(Folder.sort_order)
    )
    folders = result.scalars().all()
    return build_tree(list(folders))


@router.post("", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    body: FolderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate parent folder belongs to user if provided
    if body.parent_id:
        parent_result = await db.execute(
            select(Folder).where(
                Folder.id == UUID(body.parent_id),
                Folder.user_id == current_user.id,
            )
        )
        if parent_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent folder not found",
            )

    folder = Folder(
        name=body.name,
        parent_id=UUID(body.parent_id) if body.parent_id else None,
        user_id=current_user.id,
    )
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder


@router.put("/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: str,
    body: FolderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Folder).where(
            Folder.id == UUID(folder_id), Folder.user_id == current_user.id
        )
    )
    folder = result.scalar_one_or_none()
    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
        )

    if body.name is not None:
        folder.name = body.name
    if body.parent_id is not None:
        # Allow setting parent_id to empty string to move to root
        if body.parent_id == "":
            folder.parent_id = None
        else:
            # Prevent moving folder into itself
            if body.parent_id == folder_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot move folder into itself",
                )
            # Validate parent belongs to user
            parent_result = await db.execute(
                select(Folder).where(
                    Folder.id == UUID(body.parent_id),
                    Folder.user_id == current_user.id,
                )
            )
            if parent_result.scalar_one_or_none() is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent folder not found",
                )
            folder.parent_id = UUID(body.parent_id)
    if body.sort_order is not None:
        folder.sort_order = body.sort_order

    folder.updated_at = func.now()
    await db.commit()
    await db.refresh(folder)
    return folder


async def _get_descendant_ids(
    db: AsyncSession, folder_id: UUID, user_id: UUID
) -> list[UUID]:
    """Recursively collect all descendant folder IDs."""
    result = await db.execute(
        select(Folder.id).where(
            Folder.parent_id == folder_id, Folder.user_id == user_id
        )
    )
    child_ids = list(result.scalars().all())
    descendant_ids = list(child_ids)
    for child_id in child_ids:
        descendant_ids.extend(await _get_descendant_ids(db, child_id, user_id))
    return descendant_ids


@router.delete("/{folder_id}", status_code=status.HTTP_200_OK)
async def delete_folder(
    folder_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Folder).where(
            Folder.id == UUID(folder_id), Folder.user_id == current_user.id
        )
    )
    folder = result.scalar_one_or_none()
    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
        )

    # Collect this folder + all descendant folder IDs
    all_folder_ids = [UUID(folder_id)]
    all_folder_ids.extend(
        await _get_descendant_ids(db, UUID(folder_id), current_user.id)
    )

    # Trash all notes in these folders
    notes_result = await db.execute(
        select(Note).where(
            Note.folder_id.in_(all_folder_ids),
            Note.user_id == current_user.id,
            Note.is_trashed == False,
        )
    )
    notes = notes_result.scalars().all()
    for note in notes:
        note.is_trashed = True
        note.trashed_at = func.now()
        note.folder_id = None

    # Delete the folder (cascades to child folders)
    await db.delete(folder)
    await db.commit()
    return {"detail": "Folder deleted", "notes_trashed": len(notes)}
