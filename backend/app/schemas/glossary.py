from pydantic import BaseModel
from typing import Optional


class ExtractGlossaryRequest(BaseModel):
    text: str
    book_id: Optional[int] = None
    first_chapter_id: Optional[int] = None


class GlossaryItemSchema(BaseModel):
    raw: str
    translated: str
    type: str


class ExtractGlossaryResponse(BaseModel):
    glossaries: list[GlossaryItemSchema]
