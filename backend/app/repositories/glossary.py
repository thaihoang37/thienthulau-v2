import uuid
from typing import Optional

from sqlmodel import Session, select, col

from app.models.glossary import Glossary


def find_by_raw_values(
    session: Session, raw_values: list[str], book_id: Optional[uuid.UUID] = None
) -> list[Glossary]:
    statement = select(Glossary).where(col(Glossary.raw).in_(raw_values))
    if book_id is not None:
        statement = statement.where(Glossary.book_id == book_id)
    return list(session.exec(statement).all())


def create_many(
    session: Session,
    items: list[dict],
    book_id: Optional[uuid.UUID] = None,
    first_chapter_id: Optional[uuid.UUID] = None,
) -> int:
    count = 0
    for item in items:
        glossary = Glossary(
            raw=item["raw"],
            translated=item["translated"],
            type=item["type"],
            book_id=book_id,
            first_chapter_id=first_chapter_id,
        )
        session.add(glossary)
        count += 1
    session.commit()
    return count


def get_by_type(
    session: Session, type: str, book_id: Optional[uuid.UUID] = None
) -> list[Glossary]:
    statement = select(Glossary).where(Glossary.type == type)
    if book_id is not None:
        statement = statement.where(Glossary.book_id == book_id)
    return list(session.exec(statement).all())


def get_all(session: Session, book_id: Optional[uuid.UUID] = None) -> list[Glossary]:
    statement = select(Glossary)
    if book_id is not None:
        statement = statement.where(Glossary.book_id == book_id)
    return list(session.exec(statement).all())
