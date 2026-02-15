import logging
import threading
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Round-robin API key manager with retry on failure."""

    def __init__(self, keys: list[str]):
        self._keys = [k.strip() for k in keys if k.strip()]
        if not self._keys:
            raise ValueError("No API keys provided")
        self._index = 0
        self._lock = threading.Lock()
        # Cache: (model, api_key) -> ChatGoogleGenerativeAI instance
        self._llm_cache: dict[tuple[str, str], ChatGoogleGenerativeAI] = {}
        logger.info(f"APIKeyManager initialized with {len(self._keys)} keys")

    @property
    def total_keys(self) -> int:
        return len(self._keys)

    def next_key(self) -> str:
        """Get the next API key in round-robin order."""
        with self._lock:
            key = self._keys[self._index % len(self._keys)]
            self._index += 1
            return key

    def get_llm(self, model: str, api_key: str) -> ChatGoogleGenerativeAI:
        """Get or create a cached ChatGoogleGenerativeAI instance."""
        cache_key = (model, api_key)
        if cache_key not in self._llm_cache:
            self._llm_cache[cache_key] = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=api_key,
            )
            logger.info(f"Created new LLM instance for model={model}, key=...{api_key[-6:]}")
        return self._llm_cache[cache_key]


# Singleton
_key_manager: Optional[APIKeyManager] = None


def get_key_manager() -> APIKeyManager:
    global _key_manager
    if _key_manager is None:
        _key_manager = APIKeyManager(settings.google_api_keys)
    return _key_manager


async def invoke_with_retry(
    messages: list,
    model: str = "gemini-3-flash-preview",
    max_retries: Optional[int] = None,
) -> str:
    """Invoke LLM with round-robin key selection and retry on failure.

    Tries each key once. If all keys fail, raises the last exception.
    """
    manager = get_key_manager()
    retries = max_retries or manager.total_keys

    last_error = None
    for attempt in range(retries):
        api_key = manager.next_key()
        key_index = (manager._index - 1) % manager.total_keys + 1
        key_suffix = api_key[-6:]
        logger.info(f"Using API key {key_index}/{manager.total_keys} (...{key_suffix}), attempt {attempt + 1}/{retries}")
        try:
            llm = manager.get_llm(model, api_key)
            result = await llm.ainvoke(messages)
            logger.info(f"LLM call succeeded (key ...{key_suffix})")
            return result
        except Exception as e:
            last_error = e
            logger.warning(
                f"LLM call failed (attempt {attempt + 1}/{retries}, key ...{key_suffix}): {e}"
            )

    logger.error(f"All {retries} LLM attempts failed")
    raise last_error
