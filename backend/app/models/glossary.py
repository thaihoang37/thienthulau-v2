import uuid as uuid_module
from typing import Optional

from sqlmodel import Field, Relationship, Column
from sqlalchemy import UniqueConstraint, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModelWithTimestamp


class Glossary(BaseModelWithTimestamp, table=True):
    __tablename__ = "glossaries"
    __table_args__ = (
        UniqueConstraint("raw", "type", "book_id", name="uq_glossaries_raw_type_book_id"),
        Index("ix_glossaries_type", "type"),
        Index("ix_glossaries_raw", "raw"),
        Index("ix_glossaries_book_id", "book_id"),
    )

    id: uuid_module.UUID = Field(
        default_factory=uuid_module.uuid4,
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid_module.uuid4),
    )
    raw: str
    translated: str
    type: str
    book_id: Optional[uuid_module.UUID] = Field(
        default=None,
        sa_column=Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=True),
    )
    first_chapter_id: Optional[uuid_module.UUID] = Field(
        default=None,
        sa_column=Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=True),
    )

    # Relationships
    book: Optional["Book"] = Relationship(back_populates="glossaries")
    first_chapter: Optional["Chapter"] = Relationship(back_populates="glossaries")


from app.models.book import Book  # noqa: E402
from app.models.chapter import Chapter  # noqa: E402
