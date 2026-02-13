from typing import Optional, List, Any

from sqlmodel import Field, Relationship, Column
from sqlalchemy import JSON, UniqueConstraint, Index

from app.models.base import BaseModelWithTimestamp


class Chapter(BaseModelWithTimestamp, table=True):
    __tablename__ = "chapters"
    __table_args__ = (
        UniqueConstraint("book_id", "order", name="uq_chapters_book_id_order"),
        Index("ix_chapters_book_id", "book_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    order: int
    paragraphs: Any = Field(sa_column=Column(JSON, nullable=False))
    book_id: int = Field(foreign_key="books.id")

    # Relationships
    book: Optional["Book"] = Relationship(back_populates="chapters")
    glossaries: List["Glossary"] = Relationship(back_populates="first_chapter")

from app.models.book import Book  # noqa: E402
from app.models.glossary import Glossary  # noqa: E402
