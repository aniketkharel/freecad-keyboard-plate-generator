# Copyright (c) 2026 eco-ergo.com
# SPDX-License-Identifier: MIT
"""Top-view preview coordinates in millimetres, with KLE Y pointing down."""
import math

from .parameters import PITCH


def rectangle(key, width=None, height=None, margin=0.0):
    x, y, w, h, angle, rx, ry, _ = key
    cx, cy = x + w / 2, y + h / 2
    half_w = (w * PITCH if width is None else width) / 2 + margin
    half_h = (h * PITCH if height is None else height) / 2 + margin
    a = math.radians(angle)
    points = []
    for dx, dy in ((-half_w, -half_h), (half_w, -half_h),
                   (half_w, half_h), (-half_w, half_h)):
        px, py = cx + dx / PITCH - rx, cy + dy / PITCH - ry
        points.append(((rx + px * math.cos(a) - py * math.sin(a)) * PITCH,
                       (ry + px * math.sin(a) + py * math.cos(a)) * PITCH))
    return points


def layout_preview(keys, margin, opening):
    envelopes = [rectangle(key, margin=margin) for key in keys]
    holes = [rectangle(key, opening, opening) for key in keys]
    points = [point for polygon in envelopes for point in polygon]
    bounds = (min(p[0] for p in points), min(p[1] for p in points),
              max(p[0] for p in points), max(p[1] for p in points))
    return envelopes, holes, bounds
