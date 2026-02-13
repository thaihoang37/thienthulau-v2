from fastapi import APIRouter

from app.api.endpoints import glossary, chapter

api_router = APIRouter()


@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}


api_router.include_router(glossary.router)
api_router.include_router(chapter.router)
