from __future__ import annotations

from .config import (
    FALLBACK_TEXT_SIZE,
    FOOTER_REGION_RATIO,
    LINE_OVERLAP_RATIO,
    MAX_PAGE_NUMBER_LENGTH,
    MIN_FOOTER_GAP_RATIO,
)

from .models import Line, PageLayout, Span


def extract_spans(page) -> list[Span]:
    spans: list[Span] = []

    for block in page["blocks"]:
        for line in block["lines"]:
            for span in line["spans"]:
                if not span["text"].strip():
                    continue
                x0, y0, x1, y1 = span["bbox"]
                spans.append(
                    Span(
                        x0,
                        y0,
                        x1,
                        y1,
                        span["text"],
                        span["font"]["name"],
                        span["font"]["size"],
                    )
                )

    return spans


def dominant_text_size(spans: list[Span]) -> float:
    """Находит доминирующий размер текста в списке спанов"""

    weight_by_size: dict[float, int] = {}

    for span in spans:
        if span.is_bold:
            continue
        size = round(span.size * 2) / 2
        weight_by_size[size] = weight_by_size.get(size, 0) + len(span.text)

    if not weight_by_size:
        return FALLBACK_TEXT_SIZE

    return max(weight_by_size.items(), key=lambda item: item[1])[0]


def group_spans_into_lines(spans: list[Span], text_size: float) -> list[Line]:
    """Группирует спаны в линии"""

    min_overlap = LINE_OVERLAP_RATIO * text_size
    lines: list[Line] = []

    for span in sorted(spans, key=lambda s: (s.y0, s.x0)):
        last = lines[-1] if lines else None
        if (
            last is not None
            and min(span.y1, last.bottom) - max(span.y0, last.top) > min_overlap
        ):
            last.spans.append(span)
        else:
            lines.append(Line([span]))

    for line in lines:
        line.spans.sort(key=lambda s: s.x0)

    lines.sort(key=lambda line: line.top)

    return lines


def strip_page_number(
    lines: list[Line], page_height: float, text_size: float
) -> list[Line]:
    """Удаляет номер страницы из списка линий"""

    if not lines:
        return lines

    footer = lines[-1]
    stripped = footer.text.strip()
    in_footer_region = footer.top >= page_height * FOOTER_REGION_RATIO
    looks_numeric = len(stripped) <= MAX_PAGE_NUMBER_LENGTH and any(
        ch.isdigit() for ch in stripped
    )
    separated = (
        len(lines) < 2
        or footer.top - lines[-2].bottom >= MIN_FOOTER_GAP_RATIO * text_size
    )

    if in_footer_region and looks_numeric and separated:
        return lines[:-1]

    return lines


def build_layout(spans: list[Span], page_height: float) -> PageLayout:
    """Строит макет страницы из списка спанов"""

    text_size = dominant_text_size(spans)
    lines = group_spans_into_lines(spans, text_size)
    lines = strip_page_number(lines, page_height, text_size)
    left_margin = min((line.left for line in lines), default=0.0)

    return PageLayout(
        lines=lines,
        text_size=text_size,
        left_margin=left_margin,
        page_height=page_height,
    )
