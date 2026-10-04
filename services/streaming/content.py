from typing import Any


def extract_text(chunk: Any) -> str:
    """Extract displayable text from common LangChain stream chunks."""

    if chunk is None:
        return ""

    if isinstance(chunk, str):
        return chunk

    if isinstance(chunk, dict):
        value = chunk.get("text")
        if isinstance(value, str):
            return value

        value = chunk.get("content")
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return _extract_blocks(value)
        return ""

    content = getattr(chunk, "content", None)

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return _extract_blocks(content)

    text = getattr(chunk, "text", None)
    if isinstance(text, str):
        return text

    return ""


def _extract_blocks(blocks: list[Any]) -> str:
    parts: list[str] = []

    for block in blocks:
        if isinstance(block, str):
            parts.append(block)
            continue

        if isinstance(block, dict):
            text = block.get("text")
            if isinstance(text, str):
                parts.append(text)
            continue

        text = getattr(block, "text", None)
        if isinstance(text, str):
            parts.append(text)

    return "".join(parts)
