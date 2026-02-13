from typing import Optional, Any

from sqlmodel import Session, select, func

from app.models.chapter import Chapter


def get_next_order(session: Session, book_id: int) -> int:
    statement = select(func.coalesce(func.max(Chapter.order), 0)).where(
        Chapter.book_id == book_id
    )
    max_order = session.exec(statement).one()
    return max_order + 1


def create(
    session: Session,
    book_id: int,
    order: int,
    paragraphs: Any,
    title: str,
) -> Chapter:
    chapter = Chapter(
        book_id=book_id,
        order=order,
        paragraphs=paragraphs,
        title=title,
    )
    session.add(chapter)
    session.commit()
    session.refresh(chapter)
    return chapter


def get_by_id(session: Session, id: int) -> Optional[Chapter]:
    return session.get(Chapter, id)


def get_by_book_id(session: Session, book_id: int) -> list[Chapter]:
    statement = select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.order)
    return list(session.exec(statement).all())
