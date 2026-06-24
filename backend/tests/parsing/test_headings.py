from __future__ import annotations

from parsing.config import UNTITLED

from parsing.headings import (
    classify_line,
    find_keyword,
    leading_bold_span,
    leading_italic_keyword,
    normalize_text,
    split_into_blocks,
    typographic_headings,
)

from parsing.models import Heading, HeadingKind, PageLayout
from builders import BOLD_FONT, ITALIC_FONT, line, span, text_line

KEYWORDS = ("Определение", "Теорема", "Лемма")


class TestNormalizeText:
    def test_lowercases_and_replaces_yo(self):
        assert normalize_text("ЛёГкий") == "легкий"


class TestFindKeyword:
    def test_finds_keyword_case_and_yo_insensitive(self):
        assert find_keyword("вот ОПРЕДЕЛЕНИЕ числа", KEYWORDS) == "Определение"

    def test_returns_none_when_absent(self):
        assert find_keyword("обычный текст", KEYWORDS) is None


class TestLeadingBoldSpan:
    def test_returns_first_bold_span(self):
        bold = span("Теорема", font=BOLD_FONT)
        assert leading_bold_span(line(bold)) is bold

    def test_returns_none_without_bold(self):
        assert leading_bold_span(text_line("plain")) is None

    def test_returns_none_when_bold_too_far(self):
        prefix = span("long prefix here ")
        bold = span("Теорема", font=BOLD_FONT)
        assert leading_bold_span(line(prefix, bold)) is None


class TestLeadingItalicKeyword:
    def test_returns_keyword_when_italic_prefix(self):
        ln = line(span("Лемма ", font=ITALIC_FONT), span("о пределе"))
        assert leading_italic_keyword(ln, KEYWORDS) == "Лемма"

    def test_returns_none_when_first_span_not_italic(self):
        ln = line(span("Лемма "), span("о пределе"))
        assert leading_italic_keyword(ln, KEYWORDS) is None

    def test_returns_none_when_no_keyword(self):
        ln = line(span("просто курсив", font=ITALIC_FONT))
        assert leading_italic_keyword(ln, KEYWORDS) is None


class TestClassifyLine:
    def test_none_when_indented_past_margin(self):
        ln = text_line("Теорема", x0=100, font=BOLD_FONT)
        assert classify_line(ln, left_margin=0, text_size=10, keywords=KEYWORDS) is None

    def test_bold_large_is_section(self):
        ln = text_line("Глава 1", x0=0, font=BOLD_FONT, size=14)  # 14 >= 10 * 1.2
        heading = classify_line(ln, 0, 10, KEYWORDS)
        assert heading == Heading(kind=HeadingKind.SECTION, title="", titled=False)

    def test_bold_normal_with_keyword_is_titled_block(self):
        ln = text_line("Определение", x0=0, font=BOLD_FONT, size=10)
        heading = classify_line(ln, 0, 10, KEYWORDS)
        assert heading == Heading(
            kind=HeadingKind.BLOCK, title="Определение", titled=True
        )

    def test_bold_normal_without_keyword_is_untitled_block(self):
        ln = text_line("Просто жирный", x0=0, font=BOLD_FONT, size=10)
        heading = classify_line(ln, 0, 10, KEYWORDS)
        assert heading == Heading(kind=HeadingKind.BLOCK, title=UNTITLED, titled=False)

    def test_italic_keyword_is_titled_block(self):
        ln = text_line("Лемма о числах", x0=0, font=ITALIC_FONT, size=10)
        heading = classify_line(ln, 0, 10, KEYWORDS)
        assert heading == Heading(kind=HeadingKind.BLOCK, title="Лемма", titled=True)

    def test_plain_line_is_not_a_heading(self):
        assert classify_line(text_line("обычный текст"), 0, 10, KEYWORDS) is None


class TestTypographicHeadings:
    def test_collects_headings_by_index(self):
        layout = PageLayout(
            lines=[
                text_line("Определение", font=BOLD_FONT, size=10),
                text_line("тело определения"),
                text_line("Теорема", font=BOLD_FONT, size=10),
            ],
            text_size=10,
            left_margin=0,
            page_height=800,
        )

        headings = typographic_headings(layout, KEYWORDS)

        assert set(headings) == {0, 2}
        assert headings[0].title == "Определение"
        assert headings[2].title == "Теорема"


class TestSplitIntoBlocks:
    def test_no_headings_makes_single_untitled_block(self):
        lines = [text_line("a"), text_line("b")]
        blocks = split_into_blocks(lines, {})

        assert len(blocks) == 1
        assert blocks[0].title == UNTITLED
        assert blocks[0].titled is False
        assert [ln.text for ln in blocks[0].lines] == ["a", "b"]

    def test_block_heading_starts_block_and_absorbs_following_lines(self):
        lines = [text_line("Определение"), text_line("тело"), text_line("ещё")]
        headings = {0: Heading(HeadingKind.BLOCK, "Определение", True)}

        blocks = split_into_blocks(lines, headings)

        assert len(blocks) == 1
        assert blocks[0].title == "Определение"
        assert len(blocks[0].lines) == 3

    def test_section_heading_resets_context_and_is_dropped(self):
        lines = [text_line("intro"), text_line("Глава"), text_line("after")]
        headings = {1: Heading(HeadingKind.SECTION, "", False)}

        blocks = split_into_blocks(lines, headings)

        assert len(blocks) == 2
        assert [ln.text for ln in blocks[0].lines] == ["intro"]
        assert [ln.text for ln in blocks[1].lines] == ["after"]
