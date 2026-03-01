import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), default="Untitled")
    body: Mapped[str] = mapped_column(Text, default="")
    folder_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("folders.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False)
    is_trashed: Mapped[bool] = mapped_column(Boolean, default=False)
    trashed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)

    user: Mapped["User"] = relationship(back_populates="notes")  # noqa: F821
    folder: Mapped["Folder | None"] = relationship(back_populates="notes")  # noqa: F821

    __table_args__ = (
        Index("ix_notes_search_vector", "search_vector", postgresql_using="gin"),
        Index("ix_notes_trash", "is_trashed", "trashed_at"),
    )
