import uuid

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.chapter import TranslateChapterRequest, TranslateChapterResponse, ChapterListItem
from app.services import chapter as chapter_service
from app.repositories import chapter as chapter_repo

router = APIRouter(prefix="/chapter", tags=["chapter"])


@router.get("/list/{book_id}", response_model=list[ChapterListItem])
def list_chapters(
    book_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    return chapter_repo.list_by_book_id(session, book_id)


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
