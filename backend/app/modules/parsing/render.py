from __future__ import annotations

import numpy as np

from .config import INK_THRESHOLD
from .models import Scope


def row_has_ink(gray: np.ndarray, row: int) -> bool:
    return bool((gray[row] < INK_THRESHOLD).any())


def grow_ink_edge(
    gray: np.ndarray, start: int, step: int, gap_tolerance: int, limit: int
) -> int:
    """Расширяет края в заданном направлении"""

    height = gray.shape[0]
    row = edge = max(0, min(start, height - 1))
    blank_run = 0

    while 0 <= row < height:
        if (step > 0 and row >= limit) or (step < 0 and row <= limit):
            break

        if row_has_ink(gray, row):
            edge = row
            blank_run = 0
        else:
            blank_run += 1
            if blank_run > gap_tolerance:
                break

        row += step

    return edge


def distance_to_ink(gray: np.ndarray, start: int, step: int) -> int:
    """Находит расстояние до ближайшего пикселя в заданном направлении"""

    height = gray.shape[0]
    row = start
    distance = 0

    while 0 <= row < height:
        if row_has_ink(gray, row):
            return distance

        row += step
        distance += 1

    return distance


def ink_scope(
    gray: np.ndarray,
    content_top: int,
    content_bottom: int,
    ceiling: int,
    floor: int,
    gap_tolerance: int,
    top_pad: int,
    bottom_pad: int,
) -> Scope:
    """Находит область пикселя в заданном диапазоне"""

    ink_top = grow_ink_edge(gray, content_top, -1, gap_tolerance, ceiling)
    ink_bottom = grow_ink_edge(gray, content_bottom, 1, gap_tolerance, floor)
    pad_above = min(top_pad, distance_to_ink(gray, ink_top - 1, -1))
    pad_below = min(bottom_pad, distance_to_ink(gray, ink_bottom + 1, 1))

    return Scope(
        top=max(ink_top - pad_above, 0), bottom=min(ink_bottom + pad_below, floor)
    )
