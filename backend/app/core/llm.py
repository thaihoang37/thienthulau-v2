import logging
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

logger = logging.getLogger(__name__)

# Cached LLM instances per model name
_llm_cache: dict[str, ChatGoogleGenerativeAI] = {}


def get_llm(model: str = "gemini-3-flash-preview") -> ChatGoogleGenerativeAI:
    """Get or create a cached ChatGoogleGenerativeAI instance."""
    if model not in _llm_cache:
        _llm_cache[model] = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=settings.GOOGLE_API_KEY,
        )
        logger.info(f"Created LLM instance for model={model}")
    return _llm_cache[model]


async def invoke_llm(
    messages: list,
    model: str = "gemini-3-flash-preview",
) -> str:
    """Invoke LLM with a single API key."""
    llm = get_llm(model)
    result = await llm.ainvoke(messages)
    return result
