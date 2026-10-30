# Copyright (c) 2026 eco-ergo.com
# SPDX-License-Identifier: MIT
"""Shared mechanical defaults and editable length property definitions."""
PITCH = 19.05
UNDERSIDE_CLIP_RELIEF = True

# name, dialog label, property group, default millimetres, property description
LENGTH_PARAMETERS = (
    ('PlateThickness', 'Plate thickness (mm)', '02 Plate', 3.0,
     'Total structural plate thickness in mm'),
    ('OutlineMargin', 'Outline margin (mm)', '02 Plate', 5.0,
     'Margin outside nominal key footprints in mm'),
    ('SwitchOpening', 'Switch opening (mm)', '03 Cherry MX', 14.0,
     'Nominal square through-hole (adjust for printer tolerance)'),
    ('ClipLipThickness', 'Retaining lip (mm)', '03 Cherry MX', 1.5,
     'Material retained at the upper face above relief pockets'),
    ('ClipReliefWidth', 'Relief width (mm)', '03 Cherry MX', 1.0,
     'Extra width outward from the two clip-side edges'),
    ('ClipReliefSpan', 'Relief span (mm)', '03 Cherry MX', 9.0,
     'Relief strip width across each clip side'),
)

OUTLINE_SHAPES = ('Follow layout', 'Rectangle')
