from __future__ import annotations

from PIL import Image

from parsing.models import Block, RenderedBlock, Scope
from builders import BOLD_FONT, ITALIC_FONT, PLAIN_FONT, block, line, span, text_line


class TestSpan:
    def test_is_bold_detects_marker(self):
        assert span("x", font=BOLD_FONT).is_bold is True
        assert span("x", font="TimesBX").is_bold is True

    def test_is_bold_false_for_plain(self):
        assert span("x", font=PLAIN_FONT).is_bold is False

    def test_is_italic_detects_marker(self):
        assert span("x", font=ITALIC_FONT).is_italic is True
        assert span("x", font="Arial-Italic").is_italic is True

    def test_is_italic_false_for_plain(self):
        assert span("x", font=PLAIN_FONT).is_italic is False


class TestLine:
    def test_text_concatenates_spans(self):
        assert line(span("foo "), span("bar")).text == "foo bar"

    def test_geometry_aggregates_spans(self):
        a = span("a", x0=10, y0=5, x1=20, y1=15)
        b = span("b", x0=30, y0=8, x1=50, y1=18)
        ln = line(a, b)

        assert ln.left == 10
        assert ln.right == 50
        assert ln.top == 5
        assert ln.bottom == 18


class TestBlock:
    def test_text_joins_lines_with_newline(self):
        blk = Block(title="t", titled=True, lines=[text_line("one"), text_line("two")])
        assert blk.text == "one\ntwo"

    def test_geometry_spans_all_lines(self):
        blk = block("t", "a", "b", "c")
        assert blk.top == 0
        assert blk.bottom == 30


class TestRenderedBlock:
    def test_box_uses_full_width_and_scope(self):
        image = Image.new("L", (120, 40), color=255)
        rendered = RenderedBlock(
            block=block("t", "a"),
            image=image,
            scope=Scope(top=5, bottom=25),
            width=120,
        )

        assert rendered.box == (0, 5, 120, 25)
