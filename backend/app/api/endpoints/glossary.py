from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.glossary import ExtractGlossaryRequest, ExtractGlossaryResponse
from app.services import glossary as glossary_service

router = APIRouter(prefix="/glossary", tags=["glossary"])


@router.post("/extract", response_model=ExtractGlossaryResponse)
async def extract_glossary(
    request: ExtractGlossaryRequest,
    session: Session = Depends(get_session),
):
    glossaries = await glossary_service.extract_glossary(
        session=session,
        text=request.text,
        book_id=request.book_id,
        first_chapter_id=request.first_chapter_id,
    )
    return ExtractGlossaryResponse(glossaries=glossaries)
