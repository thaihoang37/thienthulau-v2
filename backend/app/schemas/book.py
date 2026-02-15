import uuid

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BookCreate(BaseModel):
    title: str
    author: str
    cover: Optional[str] = None
    banner: Optional[str] = None
    introduce: Optional[str] = None


class BookResponse(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    cover: Optional[str] = None
    banner: Optional[str] = None
    introduce: Optional[str] = None
    created_date: datetime
    updated_date: datetime
