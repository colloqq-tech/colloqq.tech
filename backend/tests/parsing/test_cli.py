from __future__ import annotations

import pytest  # type: ignore

pytest.importorskip("pypdfium2")
pytest.importorskip("pdftext")

from parsing.cli import parse_page_ranges, slugify


class TestSlugify:
    def test_keeps_alphanumerics_and_prefixes_index(self):
        assert slugify("Определение", 1) == "01-определение"

    def test_replaces_separators_and_collapses_dashes(self):
        assert slugify("Hello, World!", 3) == "03-hello-world"

    def test_falls_back_to_block_for_empty_slug(self):
        assert slugify("", 5) == "05-block"
        assert slugify("***", 2) == "02-block"


class TestParsePageRanges:
    def test_none_returns_all_pages(self):
        assert parse_page_ranges(None, 3) == [0, 1, 2]

    def test_parses_inclusive_range(self):
        assert parse_page_ranges("1-3", 10) == [0, 1, 2]

    def test_parses_comma_list(self):
        assert parse_page_ranges("2,4", 10) == [1, 3]

    def test_mixes_ranges_and_singletons(self):
        assert parse_page_ranges("1-3,5", 10) == [0, 1, 2, 4]

    def test_filters_out_of_bounds(self):
        assert parse_page_ranges("100", 5) == []
