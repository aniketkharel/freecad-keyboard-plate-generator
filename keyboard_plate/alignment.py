# Copyright (c) 2026 eco-ergo.com
# SPDX-License-Identifier: MIT
"""Alignment offsets in FreeCAD XY coordinates, independent of FreeCAD."""


def alignment_offset(bounds, reference):
    """Bounds are minimum X/Y and maximum X/Y in model coordinates."""
    left, bottom, right, top = bounds
    if reference == 'Keep layout coordinates':
        return 0.0, 0.0
    if reference == 'Center on origin':
        return -(left + right) / 2, -(bottom + top) / 2
    if reference == 'Corner at origin':
        return -left, -bottom
    raise ValueError('Unknown placement reference: %s' % reference)
