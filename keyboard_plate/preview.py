# Copyright (c) 2026 eco-ergo.com
# SPDX-License-Identifier: MIT
"""Top-view preview coordinates in millimetres, with KLE Y pointing down."""
import math

from .parameters import PITCH
from .alignment import alignment_offset


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


def layout_preview(keys, margin, opening, outline_shape='Follow layout',
                   placement_reference='Keep layout coordinates'):
    envelopes = [rectangle(key, margin=margin) for key in keys]
    holes = [rectangle(key, opening, opening) for key in keys]
    points = [point for polygon in envelopes for point in polygon]
    bounds = (min(p[0] for p in points), min(p[1] for p in points),
              max(p[0] for p in points), max(p[1] for p in points))
    if outline_shape == 'Rectangle':
        left, top, right, bottom = bounds
        envelopes = [[(left, top), (right, top), (right, bottom), (left, bottom)]]
    elif outline_shape != 'Follow layout':
        raise ValueError('Unknown outline shape: %s' % outline_shape)
    left, top, right, bottom = bounds
    # Preview uses screen-down Y; model bounds use positive-up Y.
    dx, dy = alignment_offset((left, -bottom, right, -top), placement_reference)
    envelopes = [[(x + dx, y - dy) for x, y in polygon] for polygon in envelopes]
    holes = [[(x + dx, y - dy) for x, y in polygon] for polygon in holes]
    bounds = (left + dx, top - dy, right + dx, bottom - dy)
    return envelopes, holes, bounds
