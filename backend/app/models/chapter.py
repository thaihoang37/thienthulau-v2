import uuid as uuid_module
from typing import Optional, List, Any

from sqlmodel import Field, Relationship, Column
from sqlalchemy import JSON, UniqueConstraint, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModelWithTimestamp


class Chapter(BaseModelWithTimestamp, table=True):
    __tablename__ = "chapters"
    __table_args__ = (
        UniqueConstraint("book_id", "order", name="uq_chapters_book_id_order"),
        Index("ix_chapters_book_id", "book_id"),
    )

    id: uuid_module.UUID = Field(
        default_factory=uuid_module.uuid4,
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid_module.uuid4),
    )
    title: Optional[Any] = Field(default=None, sa_column=Column(JSON, nullable=True))
    order: Optional[int] = None
    summary: Optional[str] = None
    paragraphs: Optional[Any] = Field(default=None, sa_column=Column(JSON, nullable=True))
    status: str = Field(default="pending")  # "pending" | "translated"
    book_id: uuid_module.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    )

    # Relationships
    book: Optional["Book"] = Relationship(back_populates="chapters")
    glossaries: List["Glossary"] = Relationship(back_populates="first_chapter")

from app.models.book import Book  # noqa: E402
from app.models.glossary import Glossary  # noqa: E402
