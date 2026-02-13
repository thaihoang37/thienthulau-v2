import json
import re
import logging
from typing import Optional

from sqlmodel import Session
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.prompts.translate_chapter import build_translate_chapter_prompt
from app.repositories import glossary as glossary_repo
from app.schemas.chapter import SentencePair

logger = logging.getLogger(__name__)


def _extract_text_content(content) -> str:
    """Extract text from LangChain response content (can be str or list of blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block["text"] for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(content)


def _split_into_paragraphs(text: str) -> list[str]:
    cleaned = text.strip()
    paragraphs = [p.strip() for p in cleaned.split("\n") if p.strip()]

    result: list[str] = []
    for para in paragraphs:
        if len(para) <= 200:
            result.append(para)
        else:
            # Split by Chinese punctuation
            sentences = re.split(r"([。！？；]+)", para)
            sentences = [s for s in sentences if s.strip()]
            current_chunk = ""

            for part in sentences:
                current_chunk += part
                if re.search(r"[。！？；]", part) and len(current_chunk) > 150:
                    result.append(current_chunk.strip())
                    current_chunk = ""

            if current_chunk.strip():
                result.append(current_chunk.strip())

    return result


def _parse_translated_sentences(response: str) -> list[str]:
    try:
        start = response.find("[")
        if start == -1:
            return []

        depth = 0
        end = -1
        for i in range(start, len(response)):
            if response[i] == "[":
                depth += 1
            elif response[i] == "]":
                depth -= 1
                if depth == 0:
                    end = i
                    break

        if end == -1:
            return []

        json_str = response[start : end + 1]
        json_str = re.sub(r",\s*\]", "]", json_str)

        parsed = json.loads(json_str)
        return parsed if isinstance(parsed, list) else []
    except Exception as e:
        logger.error(f"Failed to parse translated sentences JSON: {e}")
        logger.error(f"Response preview: {response[:500]}")
        return []


async def translate_chapter(
    session: Session,
    text: str,
    book_id: Optional[int] = None,
) -> list[SentencePair]:
    raw_paragraphs = _split_into_paragraphs(text)

    logger.info(f"Split into {len(raw_paragraphs)} paragraphs")

    # Load glossary from DB if book_id provided
    glossary = None
    if book_id is not None:
        glossary_items = glossary_repo.get_all(session, book_id)
        if glossary_items:
            glossary = [
                {"raw": g.raw, "translated": g.translated, "type": g.type}
                for g in glossary_items
            ]
            logger.info(f"Loaded {len(glossary)} glossary items for book {book_id}")

    system_prompt = build_translate_chapter_prompt(glossary)

    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=settings.GOOGLE_API_KEY,
    )

    messages = [
        ("system", system_prompt),
        ("human", json.dumps(raw_paragraphs, ensure_ascii=False)),
    ]

    result = await llm.ainvoke(messages)
    text_content = _extract_text_content(result.content)
    translated_paragraphs = _parse_translated_sentences(text_content)

    sentences = [
        SentencePair(
            raw=raw,
            translated=(
                translated_paragraphs[i]
                if i < len(translated_paragraphs)
                else f"[Translation error: paragraph {i + 1}]"
            ),
        )
        for i, raw in enumerate(raw_paragraphs)
    ]

    return sentences
