from pydantic import BaseModel
from typing import Optional


class TranslateChapterRequest(BaseModel):
    text: str
    book_id: Optional[int] = None


class SentencePair(BaseModel):
    raw: str
    translated: str


class TranslateChapterResponse(BaseModel):
    sentences: list[SentencePair]
