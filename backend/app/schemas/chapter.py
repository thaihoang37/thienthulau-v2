import uuid

from pydantic import BaseModel
from typing import Optional


class TranslateChapterRequest(BaseModel):
    text: str
    book_id: Optional[uuid.UUID] = None
    chapter_id: Optional[uuid.UUID] = None


class SentencePair(BaseModel):
    raw: str
    translated: str


class ChapterTitle(BaseModel):
    raw: str
    translated: str


class TranslateChapterResponse(BaseModel):
    chapter_id: Optional[uuid.UUID] = None
    title: Optional[ChapterTitle] = None
    order: Optional[int] = None
    summary: Optional[str] = None
    sentences: list[SentencePair]


class ChapterListItem(BaseModel):
    id: uuid.UUID
    title: Optional[dict] = None
    order: Optional[int] = None


class ChapterDetailResponse(BaseModel):
    id: uuid.UUID
    title: Optional[str] = None
    order: Optional[int] = None
    summary: Optional[str] = None
    paragraphs: list[str] = []
    prev_order: Optional[int] = None
    next_order: Optional[int] = None
