from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FolderCreate(BaseModel):
    name: str
    parent_id: str | None = None


class FolderUpdate(BaseModel):
    name: str | None = None
    parent_id: str | None = None
    sort_order: int | None = None


class FolderResponse(BaseModel):
    id: UUID
    name: str
    parent_id: UUID | None
    user_id: UUID
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FolderTreeResponse(BaseModel):
    id: UUID
    name: str
    parent_id: UUID | None
    sort_order: int
    created_at: datetime
    updated_at: datetime
    children: list[FolderTreeResponse] = []

    model_config = {"from_attributes": True}
