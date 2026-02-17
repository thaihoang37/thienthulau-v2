import uuid

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from fastapi import HTTPException

from app.schemas.chapter import (
    TranslateChapterRequest,
    TranslateChapterResponse,
    ChapterListItem,
    ChapterDetailResponse,
)
from app.services import chapter as chapter_service
from app.repositories import chapter as chapter_repo

router = APIRouter(prefix="/chapter", tags=["chapter"])


@router.get("/list/{book_id}", response_model=list[ChapterListItem])
def list_chapters(
    book_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    return chapter_repo.list_by_book_id(session, book_id)


@router.get("/{book_id}/{order}", response_model=ChapterDetailResponse)
def get_chapter(
    book_id: uuid.UUID,
    order: int,
    session: Session = Depends(get_session),
):
    chapter = chapter_repo.get_by_book_and_order(session, book_id, order)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Extract only translated text from paragraphs
    translated_paragraphs: list[str] = []
    if chapter.paragraphs:
        for p in chapter.paragraphs:
            if isinstance(p, dict):
                translated_paragraphs.append(p.get("translated", p.get("raw", "")))
            elif isinstance(p, str):
                translated_paragraphs.append(p)

    # Get translated title
    title_text = None
    if chapter.title:
        if isinstance(chapter.title, dict):
            title_text = chapter.title.get("translated", chapter.title.get("raw"))
        elif isinstance(chapter.title, str):
            title_text = chapter.title

    prev_order, next_order = chapter_repo.get_adjacent_orders(session, book_id, order)

    return ChapterDetailResponse(
        id=chapter.id,
        title=title_text,
        order=chapter.order,
        summary=chapter.summary,
        paragraphs=translated_paragraphs,
        prev_order=prev_order,
        next_order=next_order,
    )


@router.post("/translate", response_model=TranslateChapterResponse)
async def translate_chapter(
    request: TranslateChapterRequest,
    session: Session = Depends(get_session),
):
    result = await chapter_service.translate_chapter(
        session=session,
        text=request.text,
        book_id=request.book_id,
        chapter_id=request.chapter_id,
    )
    return TranslateChapterResponse(
        sentences=result["sentences"],
        chapter_id=result["chapter_id"],
        title=result["title"],
        order=result["order"],
        summary=result["summary"],
    )
