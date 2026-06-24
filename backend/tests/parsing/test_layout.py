from __future__ import annotations

from parsing.config import FALLBACK_TEXT_SIZE

from parsing.layout import (
    build_layout,
    dominant_text_size,
    extract_spans,
    group_spans_into_lines,
    strip_page_number,
)

from builders import BOLD_FONT, page_dict, page_span, span, text_line


class TestExtractSpans:
    def test_reads_spans_and_skips_blank_text(self):
        page = page_dict(
            [
                [
                    page_span("hello", (0, 0, 30, 10)),
                    page_span("   ", (30, 0, 40, 10)),
                ]
            ]
        )

        spans = extract_spans(page)

        assert len(spans) == 1
        assert spans[0].text == "hello"
        assert (spans[0].x0, spans[0].y0, spans[0].x1, spans[0].y1) == (0, 0, 30, 10)


class TestDominantTextSize:
    def test_returns_fallback_when_no_plain_spans(self):
        assert dominant_text_size([span("x", font=BOLD_FONT)]) == FALLBACK_TEXT_SIZE

    def test_ignores_bold_and_weights_by_text_length(self):
        spans = [
            span("aaaaaa", size=10.0),
            span("bb", size=12.0),
            span("HEADING", size=20.0, font=BOLD_FONT),
        ]
        assert dominant_text_size(spans) == 10.0

    def test_rounds_size_to_half_point(self):
        assert dominant_text_size([span("text", size=10.2)]) == 10.0
        assert dominant_text_size([span("text", size=10.3)]) == 10.5


class TestGroupSpansIntoLines:
    def test_groups_vertically_overlapping_spans(self):
        spans = [
            span("b", x0=40, y0=0, y1=10),
            span("a", x0=0, y0=1, y1=11),
        ]

        lines = group_spans_into_lines(spans, text_size=10.0)

        assert len(lines) == 1
        assert lines[0].text == "ab"

    def test_separates_non_overlapping_rows_sorted_by_top(self):
        spans = [
            span("second", x0=0, y0=100, y1=110),
            span("first", x0=0, y0=0, y1=10),
        ]

        lines = group_spans_into_lines(spans, text_size=10.0)

        assert [ln.text for ln in lines] == ["first", "second"]


class TestStripPageNumber:
    def test_returns_empty_for_empty_input(self):
        assert strip_page_number([], page_height=800, text_size=10) == []

    def test_drops_separated_numeric_footer(self):
        lines = [
            text_line("body", y0=600),
            text_line("12", y0=760),
        ]
        assert len(strip_page_number(lines, 800, 10)) == 1

    def test_keeps_footer_outside_region(self):
        lines = [text_line("body", y0=100), text_line("12", y0=300)]
        assert len(strip_page_number(lines, 800, 10)) == 2

    def test_keeps_long_footer_text(self):
        lines = [
            text_line("body", y0=600),
            text_line("это не номер страницы", y0=760),
        ]
        assert len(strip_page_number(lines, 800, 10)) == 2

    def test_keeps_footer_glued_to_body(self):
        lines = [text_line("body", y0=745), text_line("12", y0=750)]
        assert len(strip_page_number(lines, 800, 10)) == 2


class TestBuildLayout:
    def test_assembles_layout_fields(self):
        spans = [
            span("Body text here", x0=20, y0=0, y1=10, size=10.0),
            span("more body words", x0=20, y0=20, y1=30, size=10.0),
        ]

        layout = build_layout(spans, page_height=800)

        assert layout.page_height == 800
        assert layout.text_size == 10.0
        assert layout.left_margin == 20
        assert len(layout.lines) == 2
