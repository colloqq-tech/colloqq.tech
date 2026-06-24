from __future__ import annotations

from parsing.models import Block, Line, Span

PLAIN_FONT = "Regular"
BOLD_FONT = "Arial-Bold"
ITALIC_FONT = "Arial-Oblique"


def span(
    text: str,
    *,
    x0: float = 0.0,
    y0: float = 0.0,
    x1: float | None = None,
    y1: float = 10.0,
    font: str = PLAIN_FONT,
    size: float = 10.0,
) -> Span:
    if x1 is None:
        x1 = x0 + max(len(text), 1) * size * 0.5

    return Span(x0=x0, y0=y0, x1=x1, y1=y1, text=text, font=font, size=size)


def line(*spans: Span) -> Line:
    return Line(list(spans))


def text_line(
    text: str,
    *,
    x0: float = 0.0,
    y0: float = 0.0,
    font: str = PLAIN_FONT,
    size: float = 10.0,
) -> Line:
    return line(span(text, x0=x0, y0=y0, y1=y0 + size, font=font, size=size))


def block(title: str, *texts: str, titled: bool = True) -> Block:
    lines = [text_line(text, y0=index * 10) for index, text in enumerate(texts)]

    return Block(title=title, titled=titled, lines=lines)


def page_span(
    text: str,
    bbox: tuple[float, float, float, float],
    *,
    font: str = PLAIN_FONT,
    size: float = 10.0,
) -> dict:
    return {"text": text, "bbox": list(bbox), "font": {"name": font, "size": size}}


def page_dict(lines: list[list[dict]], *, height: float = 800.0, page: int = 0) -> dict:
    return {
        "page": page,
        "height": height,
        "blocks": [{"lines": [{"spans": spans} for spans in lines]}],
    }
