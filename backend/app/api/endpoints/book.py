from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.book import BookCreate, BookResponse
from app.services import book as book_service

router = APIRouter(prefix="/books", tags=["books"])


@router.post("", response_model=BookResponse)
def create_book(
    request: BookCreate,
    session: Session = Depends(get_session),
):
    book = book_service.create_book(session=session, data=request)
    return book
