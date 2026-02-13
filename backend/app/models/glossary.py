from typing import Optional

from sqlmodel import Field, Relationship
from sqlalchemy import UniqueConstraint, Index

from app.models.base import BaseModelWithTimestamp


class Glossary(BaseModelWithTimestamp, table=True):
    __tablename__ = "glossaries"
    __table_args__ = (
        UniqueConstraint("raw", "type", "book_id", name="uq_glossaries_raw_type_book_id"),
        Index("ix_glossaries_type", "type"),
        Index("ix_glossaries_raw", "raw"),
        Index("ix_glossaries_book_id", "book_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    raw: str
    translated: str
    type: str
    book_id: Optional[int] = Field(default=None, foreign_key="books.id")
    first_chapter_id: Optional[int] = Field(default=None, foreign_key="chapters.id")

    # Relationships
    book: Optional["Book"] = Relationship(back_populates="glossaries")
    first_chapter: Optional["Chapter"] = Relationship(back_populates="glossaries")


from app.models.book import Book  # noqa: E402
from app.models.chapter import Chapter  # noqa: E402
