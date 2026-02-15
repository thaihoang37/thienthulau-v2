import uuid

from pydantic import BaseModel
from typing import Optional


class TranslateChapterRequest(BaseModel):
    text: str
    book_id: Optional[uuid.UUID] = None
    title: Optional[str] = None


class SentencePair(BaseModel):
    raw: str
    translated: str


class TranslateChapterResponse(BaseModel):
    chapter_id: Optional[uuid.UUID] = None
    sentences: list[SentencePair]
