import json
import logging
import uuid
from typing import Optional

from sqlmodel import Session

from app.core.llm import invoke_llm
from app.prompts.extract_glossary import EXTRACT_GLOSSARY_PROMPT
from app.repositories import glossary as glossary_repo
from app.repositories import chapter as chapter_repo
from app.schemas.glossary import GlossaryItemSchema

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


def _parse_glossary_from_response(response: str) -> list[dict]:
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
        # Remove trailing comma before closing bracket
        import re
        json_str = re.sub(r",\s*\]", "]", json_str)

        parsed = json.loads(json_str)
        return parsed if isinstance(parsed, list) else []
    except Exception as e:
        logger.error(f"Failed to parse glossary JSON: {e}")
        logger.error(f"Response preview: {response[:500]}")
        return []


async def extract_glossary(
    session: Session,
    text: str,
    book_id: Optional[uuid.UUID] = None,
    first_chapter_id: Optional[uuid.UUID] = None,
) -> dict:
    # Create a placeholder chapter if book_id is provided and no chapter_id yet
    chapter_id = first_chapter_id
    if book_id is not None and chapter_id is None:
        placeholder = chapter_repo.create_placeholder(session, book_id)
        chapter_id = placeholder.id
        logger.info(f"Created placeholder chapter {chapter_id} for book {book_id}")

    messages = [
        ("system", EXTRACT_GLOSSARY_PROMPT),
        ("human", f"Chapter raw:\n---\n{text}\n---"),
    ]

    result = await invoke_llm(messages)
    text_content = _extract_text_content(result.content)
    extracted_items = _parse_glossary_from_response(text_content)

    if not extracted_items:
        return {"glossaries": [], "chapter_id": chapter_id}

    # Dedup against existing DB records
    raw_values = [item["raw"] for item in extracted_items]
    existing_items = glossary_repo.find_by_raw_values(session, raw_values, book_id)
    existing_raw_set = {item.raw for item in existing_items}

    new_items = [item for item in extracted_items if item["raw"] not in existing_raw_set]

    if new_items:
        saved_count = glossary_repo.create_many(session, new_items, book_id, chapter_id)
        logger.info(f"Saved {saved_count} new glossary items (skipped {len(existing_raw_set)} existing)")

    # Combine all glossaries
    glossaries = [
        GlossaryItemSchema(raw=item.raw, translated=item.translated, type=item.type)
        for item in existing_items
    ] + [
        GlossaryItemSchema(**item) for item in new_items
    ]

    return {"glossaries": glossaries, "chapter_id": chapter_id}

