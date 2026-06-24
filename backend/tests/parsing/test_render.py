from __future__ import annotations

import numpy as np

from parsing.render import distance_to_ink, grow_ink_edge, ink_scope, row_has_ink

WHITE = 255
INK = 0  # < INK_THRESHOLD (200)


def gray_with_ink(
    height: int, ink_rows: range | list[int], width: int = 4
) -> np.ndarray:
    gray = np.full((height, width), WHITE, dtype=np.uint8)

    for row in ink_rows:
        gray[row] = INK

    return gray


class TestRowHasInk:
    def test_detects_ink_and_blank_rows(self):
        gray = gray_with_ink(3, [1])
        assert row_has_ink(gray, 1) is True
        assert row_has_ink(gray, 0) is False


class TestGrowInkEdge:
    def test_grows_down_until_gap_exceeds_tolerance(self):
        gray = gray_with_ink(20, [10, 11, 12])
        edge = grow_ink_edge(gray, start=10, step=1, gap_tolerance=1, limit=20)
        assert edge == 12

    def test_grows_up_until_gap_exceeds_tolerance(self):
        gray = gray_with_ink(20, [8, 9, 10])
        edge = grow_ink_edge(gray, start=10, step=-1, gap_tolerance=1, limit=0)
        assert edge == 8

    def test_stops_at_limit(self):
        gray = gray_with_ink(20, range(0, 20))
        edge = grow_ink_edge(gray, start=10, step=1, gap_tolerance=1, limit=15)
        assert edge == 14


class TestDistanceToInk:
    def test_zero_when_start_is_ink(self):
        gray = gray_with_ink(10, [5])
        assert distance_to_ink(gray, start=5, step=1) == 0

    def test_counts_rows_until_ink(self):
        gray = gray_with_ink(10, [5])
        assert distance_to_ink(gray, start=2, step=1) == 3

    def test_returns_distance_to_edge_when_no_ink(self):
        gray = gray_with_ink(10, [])
        assert distance_to_ink(gray, start=8, step=1) == 2


class TestInkScope:
    def test_wraps_content_with_padding(self):
        gray = gray_with_ink(60, range(20, 31))
        scope = ink_scope(
            gray,
            content_top=20,
            content_bottom=30,
            ceiling=0,
            floor=60,
            gap_tolerance=2,
            top_pad=5,
            bottom_pad=5,
        )

        assert scope.top == 15
        assert scope.bottom == 35

    def test_padding_limited_by_nearby_ink(self):
        gray = gray_with_ink(60, [18, *range(20, 31)])
        scope = ink_scope(
            gray,
            content_top=20,
            content_bottom=30,
            ceiling=0,
            floor=60,
            gap_tolerance=0,
            top_pad=5,
            bottom_pad=5,
        )

        assert scope.top == 19
        assert scope.bottom == 35
