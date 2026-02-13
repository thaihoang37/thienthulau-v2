from typing import Optional, List

from sqlmodel import Field, Relationship

from app.models.base import BaseModelWithTimestamp


class Book(BaseModelWithTimestamp, table=True):
    __tablename__ = "books"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    cover: Optional[str] = None
    banner: Optional[str] = None

    # Relationships
    chapters: List["Chapter"] = Relationship(back_populates="book")
    glossaries: List["Glossary"] = Relationship(back_populates="book")


# Avoid circular imports
from app.models.chapter import Chapter  # noqa: E402
from app.models.glossary import Glossary  # noqa: E402
