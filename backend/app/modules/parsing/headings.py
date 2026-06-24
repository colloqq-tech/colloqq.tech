from __future__ import annotations

from typing import Sequence

from .config import (
    LEFT_MARGIN_TOLERANCE,
    MAX_PREFIX_BEFORE_HEADING,
    SECTION_HEADING_SIZE_RATIO,
    UNTITLED,
)

from .models import Block, Heading, HeadingKind, Line, PageLayout, Span


def normalize_text(text: str) -> str:
    return text.lower().replace("ё", "е")


def find_keyword(text: str, keywords: Sequence[str]) -> str | None:
    normalized = normalize_text(text)

    for keyword in keywords:
        if normalize_text(keyword) in normalized:
            return keyword

    return None


def leading_bold_span(line: Line) -> Span | None:
    """Находит первый жирный span в строке"""

    prefix_length = 0

    for span in line.spans:
        if span.is_bold:
            return span

        prefix_length += len(span.text.strip())

        if prefix_length > MAX_PREFIX_BEFORE_HEADING:
            return None

    return None


def leading_italic_keyword(line: Line, keywords: Sequence[str]) -> str | None:
    """Находит первое курсивное ключевое слово в строке"""

    if not line.spans[0].is_italic:
        return None

    head = normalize_text(line.text).lstrip()

    for keyword in keywords:
        if head.startswith(normalize_text(keyword)):
            return keyword

    return None


def classify_line(
    line: Line, left_margin: float, text_size: float, keywords: Sequence[str]
) -> Heading | None:
    """Классифицирует строку как заголовок"""

    if line.left > left_margin + LEFT_MARGIN_TOLERANCE:
        return None

    bold_span = leading_bold_span(line)

    if bold_span is not None:
        if bold_span.size >= text_size * SECTION_HEADING_SIZE_RATIO:
            return Heading(kind=HeadingKind.SECTION, title="", titled=False)

        keyword = find_keyword(line.text, keywords)

        return Heading(
            kind=HeadingKind.BLOCK,
            title=keyword or UNTITLED,
            titled=keyword is not None,
        )

    keyword = leading_italic_keyword(line, keywords)

    if keyword is not None:
        return Heading(kind=HeadingKind.BLOCK, title=keyword, titled=True)

    return None


def typographic_headings(
    layout: PageLayout, keywords: Sequence[str]
) -> dict[int, Heading]:
    """Находит заголовки в макете страницы"""

    headings: dict[int, Heading] = {}

    for index, line in enumerate(layout.lines):
        heading = classify_line(line, layout.left_margin, layout.text_size, keywords)
        if heading is not None:
            headings[index] = heading

    return headings


def split_into_blocks(lines: list[Line], headings: dict[int, Heading]) -> list[Block]:
    """Разбивает линии на блоки по заголовкам"""

    blocks: list[Block] = []
    current: Block | None = None

    for index, line in enumerate(lines):
        heading = headings.get(index)

        if heading is not None and heading.kind is HeadingKind.SECTION:
            current = None
        elif heading is not None:
            current = Block(title=heading.title, titled=heading.titled, lines=[line])
            blocks.append(current)
        elif current is not None:
            current.lines.append(line)
        else:
            current = Block(title=UNTITLED, titled=False, lines=[line])
            blocks.append(current)

    return blocks
