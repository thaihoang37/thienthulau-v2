from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.chapter import TranslateChapterRequest, TranslateChapterResponse
from app.services import chapter as chapter_service

router = APIRouter(prefix="/chapter", tags=["chapter"])


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
