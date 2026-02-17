import json
import re
import logging
import uuid
from typing import Optional

from sqlmodel import Session

from app.core.llm import invoke_llm
from app.prompts.translate_chapter import build_translate_chapter_prompt
from app.repositories import glossary as glossary_repo
from app.repositories import chapter as chapter_repo
from app.schemas.chapter import SentencePair, ChapterTitle

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


def _parse_translation_response(response: str) -> dict:
    """Parse LLM response into a dict with translations, summary, title_raw, title_translated, order."""
    try:
        # Try to find JSON object: {"translations": [...], "summary": "...", ...}
        obj_start = response.find("{")
        if obj_start != -1:
            depth = 0
            obj_end = -1
            for i in range(obj_start, len(response)):
                if response[i] == "{":
                    depth += 1
                elif response[i] == "}":
                    depth -= 1
                    if depth == 0:
                        obj_end = i
                        break

            if obj_end != -1:
                json_str = response[obj_start : obj_end + 1]
                json_str = re.sub(r",\s*]", "]", json_str)
                json_str = re.sub(r",\s*}", "}", json_str)
                parsed = json.loads(json_str)
                if isinstance(parsed, dict):
                    return parsed

        # Fallback: try to find a plain JSON array
        arr_start = response.find("[")
        if arr_start == -1:
            return {}

        depth = 0
        arr_end = -1
        for i in range(arr_start, len(response)):
            if response[i] == "[":
                depth += 1
            elif response[i] == "]":
                depth -= 1
                if depth == 0:
                    arr_end = i
                    break

        if arr_end == -1:
            return {}

        json_str = response[arr_start : arr_end + 1]
        json_str = re.sub(r",\s*]", "]", json_str)
        parsed = json.loads(json_str)
        return {"translations": parsed if isinstance(parsed, list) else []}
    except Exception as e:
        logger.error(f"Failed to parse translation response JSON: {e}")
        logger.error(f"Response preview: {response[:500]}")
        return {}


DEFAULT_BOOK_ID = uuid.UUID("7d274da0-2b6e-4571-b575-ffb4227c8181")


async def translate_chapter(
    session: Session,
    text: str,
    book_id: Optional[uuid.UUID] = None,
    chapter_id: Optional[uuid.UUID] = None,
) -> dict:
    if book_id is None:
        book_id = DEFAULT_BOOK_ID
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

    messages = [
        ("system", system_prompt),
        ("human", json.dumps(raw_paragraphs, ensure_ascii=False)),
    ]

    result = await invoke_llm(messages)
    text_content = _extract_text_content(result.content)
    parsed = _parse_translation_response(text_content)

    translated_paragraphs = parsed.get("translations", [])
    summary = parsed.get("summary")
    title_raw = parsed.get("title_raw")
    title_translated = parsed.get("title_translated")
    order_from_llm = parsed.get("order")

    # Remove the title line from raw_paragraphs (LLM excluded it from translations)
    content_paragraphs = [p for p in raw_paragraphs if p.strip() != (title_raw or "").strip()] if title_raw else raw_paragraphs

    sentences = [
        SentencePair(
            raw=raw,
            translated=(
                translated_paragraphs[i]
                if i < len(translated_paragraphs)
                else f"[Translation error: paragraph {i + 1}]"
            ),
        )
        for i, raw in enumerate(content_paragraphs)
    ]

    # Build title object
    title = None
    if title_raw or title_translated:
        title = ChapterTitle(
            raw=title_raw or "",
            translated=title_translated or "",
        )

    # Persist to DB
    result_chapter_id = chapter_id
    if book_id is not None:
        order = order_from_llm if isinstance(order_from_llm, int) and order_from_llm > 0 else chapter_repo.get_next_order(session, book_id)
        order = order - 6 # Only for TCKV
        paragraphs = [s.model_dump() for s in sentences]
        title_data = title.model_dump() if title else {"raw": "", "translated": ""}

        if chapter_id is not None:
            # Update existing placeholder chapter
            chapter = chapter_repo.update_translation(
                session=session,
                chapter_id=chapter_id,
                order=order,
                paragraphs=paragraphs,
                title=title_data,
                summary=summary,
            )
            if chapter:
                result_chapter_id = chapter.id
                logger.info(f"Updated placeholder chapter {chapter_id} (order={order}) for book {book_id}")
            else:
                logger.warning(f"Chapter {chapter_id} not found, creating new one")
                chapter = chapter_repo.create(
                    session=session,
                    book_id=book_id,
                    order=order,
                    paragraphs=paragraphs,
                    title=title_data,
                    summary=summary,
                )
                result_chapter_id = chapter.id
        else:
            # Create new chapter (no placeholder)
            chapter = chapter_repo.create(
                session=session,
                book_id=book_id,
                order=order,
                paragraphs=paragraphs,
                title=title_data,
                summary=summary,
            )
            result_chapter_id = chapter.id
            logger.info(f"Saved chapter {result_chapter_id} (order={order}) for book {book_id}")

    return {
        "sentences": sentences,
        "chapter_id": result_chapter_id,
        "title": title,
        "order": order_from_llm,
        "summary": summary,
    }

