from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Sequence

import numpy as np
from PIL import Image

from .config import BOLD_FONT_MARKERS, ITALIC_FONT_MARKERS


class HeadingKind(Enum):
    BLOCK = "block"
    SECTION = "section"


@dataclass
class Span:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    font: str
    size: float

    @property
    def is_bold(self) -> bool:
        return any(marker in self.font.upper() for marker in BOLD_FONT_MARKERS)

    @property
    def is_italic(self) -> bool:
        return any(marker in self.font.upper() for marker in ITALIC_FONT_MARKERS)


@dataclass
class Line:
    spans: list[Span]

    @property
    def text(self) -> str:
        return "".join(span.text for span in self.spans)

    @property
    def left(self) -> float:
        return min(span.x0 for span in self.spans)

    @property
    def right(self) -> float:
        return max(span.x1 for span in self.spans)

    @property
    def top(self) -> float:
        return min(span.y0 for span in self.spans)

    @property
    def bottom(self) -> float:
        return max(span.y1 for span in self.spans)


@dataclass
class Heading:
    kind: HeadingKind
    title: str
    titled: bool


@dataclass
class Block:
    title: str
    titled: bool
    lines: list[Line]

    @property
    def text(self) -> str:
        return "\n".join(line.text for line in self.lines)

    @property
    def top(self) -> float:
        return min(line.top for line in self.lines)

    @property
    def bottom(self) -> float:
        return max(line.bottom for line in self.lines)


@dataclass
class Scope:
    top: int
    bottom: int


@dataclass
class PageLayout:
    lines: list[Line]
    text_size: float
    left_margin: float
    page_height: float


@dataclass
class RenderContext:
    image: Image.Image
    gray: np.ndarray
    scale: float
    page_height: int


@dataclass
class RenderedBlock:
    block: Block
    image: Image.Image
    scope: Scope
    width: int

    @property
    def box(self) -> tuple[int, int, int, int]:
        return (0, self.scope.top, self.width, self.scope.bottom)


HeadingDetector = Callable[[PageLayout, Sequence[str]], dict[int, Heading]]
BlockFilter = Callable[[Block], bool]
ScopeRefiner = Callable[[Block, Scope, RenderContext], Scope]
