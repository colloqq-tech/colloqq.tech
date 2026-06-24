from __future__ import annotations

import numpy as np
from PIL import Image

from parsing.config import UNTITLED
from parsing.models import Block, Line
from parsing.segmenter import Segmenter
from builders import BOLD_FONT, page_dict, page_span, span, text_line


class TestSegment:
    def test_returns_empty_for_page_without_spans(self):
        assert Segmenter().segment(page_dict([])) == []

    def test_splits_page_into_titled_blocks(self):
        page = page_dict(
            [
                [page_span("Определение", (0, 0, 80, 10), font=BOLD_FONT)],
                [page_span("единицы измерения", (0, 12, 120, 22))],
                [page_span("Теорема", (0, 30, 60, 40), font=BOLD_FONT)],
                [page_span("формулировка теоремы", (0, 42, 150, 52))],
            ]
        )

        blocks = Segmenter().segment(page)

        assert [b.title for b in blocks] == ["Определение", "Теорема"]
        assert all(b.titled for b in blocks)
        assert blocks[0].lines[1].text == "единицы измерения"

    def test_keep_block_filter_drops_blocks(self):
        page = page_dict(
            [
                [page_span("Определение", (0, 0, 80, 10), font=BOLD_FONT)],
                [page_span("просто текст без заголовка", (0, 30, 200, 40))],
            ]
        )

        keep_titled = Segmenter(keep_block=lambda block: block.titled)
        blocks = keep_titled.segment(page)

        assert [b.title for b in blocks] == ["Определение"]

    def test_custom_heading_detector_is_used(self):
        page = page_dict([[page_span("anything", (0, 0, 50, 10))]])
        called = {}

        def detector(layout, keywords):
            called["yes"] = True
            return {}

        Segmenter(detect_headings=detector).segment(page)

        assert called.get("yes") is True


class _FakeRender:
    def __init__(self, image: Image.Image):
        self._image = image

    def to_pil(self) -> Image.Image:
        return self._image


class _FakePdfPage:
    def __init__(self, image: Image.Image):
        self._image = image

    def render(self, scale: float) -> _FakeRender:
        return _FakeRender(self._image)


class TestRender:
    def test_renders_block_crop_within_bounds(self):
        height, width = 60, 100
        pixels = np.full((height, width), 255, dtype=np.uint8)
        pixels[20:31] = 0
        image = Image.fromarray(pixels, mode="L").convert("RGB")

        block = Block(
            title="Определение",
            titled=True,
            lines=[Line(text_line("тело", y0=20).spans)],
        )

        rendered = Segmenter(dpi=72).render([block], _FakePdfPage(image))

        assert len(rendered) == 1
        result = rendered[0]
        assert result.width == width
        assert result.block.title == "Определение"
        assert 0 <= result.scope.top < result.scope.bottom <= height
        assert result.image.size == (width, result.scope.bottom - result.scope.top)

    def test_skips_blocks_thinner_than_min_crop_height(self):
        height, width = 60, 100
        image = Image.new("RGB", (width, height), color=(255, 255, 255))

        block = Block(
            title=UNTITLED, titled=False, lines=[Line([span("x", y0=20, y1=20)])]
        )

        rendered = Segmenter(dpi=72, top_pad=0, bottom_pad=0).render(
            [block], _FakePdfPage(image)
        )

        assert rendered == []
