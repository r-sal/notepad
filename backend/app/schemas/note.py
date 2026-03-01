from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NoteCreate(BaseModel):
    title: str = "Untitled"
    body: str = ""
    folder_id: str | None = None


class NoteUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    folder_id: str | None = None
    is_starred: bool | None = None


class NoteResponse(BaseModel):
    id: UUID
    title: str
    body: str
    folder_id: UUID | None
    user_id: UUID
    is_starred: bool
    is_trashed: bool
    trashed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NoteListResponse(BaseModel):
    id: UUID
    title: str
    body: str
    folder_id: UUID | None
    is_starred: bool
    is_trashed: bool
    trashed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
