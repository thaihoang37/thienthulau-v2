from sqlmodel import Session

from app.models.book import Book
from app.repositories import book as book_repo
from app.schemas.book import BookCreate


def create_book(session: Session, data: BookCreate) -> Book:
    return book_repo.create(session, data)
