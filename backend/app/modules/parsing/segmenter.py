from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .config import (
    DEFAULT_BOTTOM_PAD,
    DEFAULT_DPI,
    DEFAULT_KEYWORDS,
    DEFAULT_TOP_PAD,
    INK_GAP_TOLERANCE_PT,
    MIN_CROP_HEIGHT,
    POINTS_PER_INCH,
)

from .headings import split_into_blocks, typographic_headings
from .layout import build_layout, extract_spans

from .models import (
    Block,
    BlockFilter,
    HeadingDetector,
    RenderContext,
    RenderedBlock,
    Scope,
    ScopeRefiner,
)

from .render import ink_scope


@dataclass
class Segmenter:
    keywords: Sequence[str] = DEFAULT_KEYWORDS
    dpi: int = DEFAULT_DPI
    top_pad: int = DEFAULT_TOP_PAD
    bottom_pad: int = DEFAULT_BOTTOM_PAD
    detect_headings: HeadingDetector = typographic_headings
    keep_block: BlockFilter | None = None
    refine_scope: ScopeRefiner | None = None

    def segment(self, page) -> list[Block]:
        spans = extract_spans(page)

        if not spans:
            return []

        layout = build_layout(spans, page["height"])
        headings = self.detect_headings(layout, self.keywords)
        blocks = split_into_blocks(layout.lines, headings)

        if self.keep_block is None:
            return blocks

        return [block for block in blocks if self.keep_block(block)]

    def render(self, blocks: list[Block], pdf_page) -> list[RenderedBlock]:
        scale = self.dpi / POINTS_PER_INCH
        image = pdf_page.render(scale=scale).to_pil()
        gray = np.asarray(image.convert("L"))
        width, height = image.size
        gap_tolerance = round(INK_GAP_TOLERANCE_PT * scale)
        extents = [
            (int(block.top * scale), int(block.bottom * scale)) for block in blocks
        ]

        context = (
            RenderContext(image=image, gray=gray, scale=scale, page_height=height)
            if self.refine_scope is not None
            else None
        )

        rendered: list[RenderedBlock] = []

        for index, block in enumerate(blocks):
            content_top, content_bottom = extents[index]
            ceiling = extents[index - 1][1] if index > 0 else 0
            floor = extents[index + 1][0] if index + 1 < len(extents) else height

            scope = ink_scope(
                gray,
                content_top,
                content_bottom,
                ceiling,
                floor,
                gap_tolerance,
                self.top_pad,
                self.bottom_pad,
            )

            if self.refine_scope is not None and context is not None:
                scope = self.refine_scope(block, scope, context)

            scope = Scope(top=max(scope.top, 0), bottom=min(scope.bottom, height))

            if scope.bottom - scope.top < MIN_CROP_HEIGHT:
                continue

            crop = image.crop((0, scope.top, width, scope.bottom))
            rendered.append(
                RenderedBlock(block=block, image=crop, scope=scope, width=width)
            )

        return rendered
