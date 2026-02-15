import uuid as uuid_module
from typing import Optional, List

from sqlmodel import Field, Relationship, Column
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModelWithTimestamp


class Book(BaseModelWithTimestamp, table=True):
    __tablename__ = "books"

    id: uuid_module.UUID = Field(
        default_factory=uuid_module.uuid4,
        sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid_module.uuid4),
    )
    title: str
    author: str
    cover: Optional[str] = None
    banner: Optional[str] = None
    introduce: Optional[str] = None

    # Relationships
    chapters: List["Chapter"] = Relationship(back_populates="book")
    glossaries: List["Glossary"] = Relationship(back_populates="book")


# Avoid circular imports
from app.models.chapter import Chapter  # noqa: E402
from app.models.glossary import Glossary  # noqa: E402
