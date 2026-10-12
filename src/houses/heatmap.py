"""Плотность домиков (только цифры, без картинок): по блокам 20x20 схемы v12 и по землям.
Картинку рисует render_heatmap.py."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import map_schema as ms  # noqa: E402


def block_counts(houses, kinds=None):
    """houses = [(X, Y, kind, ...)] -> массив 63x63: сколько домиков в блоке (bx, by)"""
    grid = np.zeros((ms.N, ms.N), int)
    for h in houses:
        X, Y, kind = h[0], h[1], h[2]
        if kinds and kind not in kinds:
            continue
        b = ms.block_of(X, Y)
        if b:
            grid[b] += 1
    return grid


def plate_counts(houses, kinds=None):
    """-> {номер земли: количество домиков}; домики вне земель (вода, вне штата) идут под ключом 0"""
    out = {}
    for h in houses:
        if kinds and h[2] not in kinds:
            continue
        n = ms.plate_of(h[0], h[1]) or 0
        out[n] = out.get(n, 0) + 1
    return out


def clusters(grid, min_count=1):
    """блоки с домиками, самые плотные сверху: [(bx, by, count)] - кандидаты на «снять вблизи с именами»"""
    pts = [(int(bx), int(by), int(grid[bx, by])) for bx, by in np.argwhere(grid >= min_count)]
    return sorted(pts, key=lambda t: -t[2])
