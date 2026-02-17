import uuid
from typing import Optional, Any

from sqlmodel import Session, select, func

from app.models.chapter import Chapter


def get_next_order(session: Session, book_id: uuid.UUID) -> int:
    statement = select(func.coalesce(func.max(Chapter.order), 0)).where(
        Chapter.book_id == book_id
    )
    max_order = session.exec(statement).one()
    return max_order + 1


def create_placeholder(session: Session, book_id: uuid.UUID) -> Chapter:
    """Create an empty chapter placeholder for glossary linking."""
    chapter = Chapter(book_id=book_id, status="pending")
    session.add(chapter)
    session.commit()
    session.refresh(chapter)
    return chapter


def update_translation(
    session: Session,
    chapter_id: uuid.UUID,
    order: int,
    paragraphs: Any,
    title: str,
    summary: Optional[str] = None,
) -> Optional[Chapter]:
    """Fill in translation data for an existing placeholder chapter."""
    chapter = session.get(Chapter, chapter_id)
    if chapter is None:
        return None
    chapter.order = order
    chapter.paragraphs = paragraphs
    chapter.title = title
    chapter.summary = summary
    chapter.status = "translated"
    session.add(chapter)
    session.commit()
    session.refresh(chapter)
    return chapter


def create(
    session: Session,
    book_id: uuid.UUID,
    order: int,
    paragraphs: Any,
    title: str,
    summary: Optional[str] = None,
) -> Chapter:
    chapter = Chapter(
        book_id=book_id,
        order=order,
        paragraphs=paragraphs,
        title=title,
        summary=summary,
        status="translated",
    )
    session.add(chapter)
    session.commit()
    session.refresh(chapter)
    return chapter


def get_by_id(session: Session, id: uuid.UUID) -> Optional[Chapter]:
    return session.get(Chapter, id)


def get_by_book_id(session: Session, book_id: uuid.UUID) -> list[Chapter]:
    statement = select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.order)
    return list(session.exec(statement).all())


def list_by_book_id(session: Session, book_id: uuid.UUID) -> list[dict]:
    """Return only title + order for chapter listing (lightweight)."""
    statement = (
        select(Chapter.title, Chapter.order)
        .where(Chapter.book_id == book_id, Chapter.status == "translated")
        .order_by(Chapter.order)
    )
    results = session.exec(statement).all()
    return [{"title": r.title, "order": r.order} for r in results]

