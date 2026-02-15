from sqlmodel import Session

from app.models.book import Book
from app.schemas.book import BookCreate


def create(session: Session, data: BookCreate) -> Book:
    book = Book(
        title=data.title,
        author=data.author,
        cover=data.cover,
        banner=data.banner,
    )
    session.add(book)
    session.commit()
    session.refresh(book)
    return book
