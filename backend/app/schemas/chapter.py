import uuid

from pydantic import BaseModel
from typing import Optional


class TranslateChapterRequest(BaseModel):
    text: str
    book_id: Optional[uuid.UUID] = None


class SentencePair(BaseModel):
    raw: str
    translated: str


class TranslateChapterResponse(BaseModel):
    sentences: list[SentencePair]
