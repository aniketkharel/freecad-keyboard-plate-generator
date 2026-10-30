# Copyright (c) 2026 eco-ergo.com
# SPDX-License-Identifier: MIT
"""Plate geometry extracted from v0.2; MX cutter construction preserved."""
import math
import FreeCAD as App
import Part
from FreeCAD import Vector
from .kle import parse_kle
from .alignment import alignment_offset

from .parameters import PITCH


def _pt(x, y, angle, rx, ry):
    """Convert KLE top-down (y positive down) to FreeCAD XY (y positive up)."""
    a = math.radians(angle)
    dx, dy = x - rx, y - ry
    x1 = rx + dx * math.cos(a) - dy * math.sin(a)
    y1 = ry + dx * math.sin(a) + dy * math.cos(a)
    return Vector(x1 * PITCH, -y1 * PITCH, 0)


def _key_polygon(key, margin):
    x, y, w, h, a, rx, ry, _ = key
    raw = [(x-margin/PITCH, y-margin/PITCH),
           (x+w+margin/PITCH, y-margin/PITCH),
           (x+w+margin/PITCH, y+h+margin/PITCH),
           (x-margin/PITCH, y+h+margin/PITCH)]
    vertices = [_pt(px, py, a, rx, ry) for px, py in raw]
    vertices.append(vertices[0])
    return Part.Face(Part.makePolygon(vertices))


def _rotated_box(cx, cy, length_x, length_y, z_start, depth, key):
    # Center and axes are defined in the key's unrotated coordinates.
    x, y, w, h, a, rx, ry, _ = key
    mid = _pt(cx, cy, a, rx, ry)
    solid = Part.makeBox(length_x, length_y, depth,
                         Vector(mid.x-length_x/2, mid.y-length_y/2, z_start))
    # Positive KLE screen rotation corresponds to negative FreeCAD Z rotation.
    # Box was centred on the already rotated target. Rotate its local orientation.
    solid.rotate(Vector(mid.x, mid.y, 0), Vector(0, 0, 1), -a)
    return solid


def _refine(shape):
    """Remove coincident coplanar seams after Boolean operations.

    It is safe to fall back to the unrefined shape if the OCC kernel cannot
    simplify a particular edge configuration.
    """
    try:
        cleaned = shape.removeSplitter()
        if not cleaned.isNull() and cleaned.isValid():
            return cleaned
    except Exception as exc:
        App.Console.PrintWarning('[Keyboard Plate] Refinement skipped: %s\n' % exc)
    return shape


def _generate(obj):
    """Create a single solid; preserve the physical geometry tested in v0.1.2.

    Positive Z is the top of the plate. The underside relief starts at z=0,
    rises to (thickness - lip), and does NOT widen the top 1.5 mm aperture.
    """
    keys = parse_kle(obj.KLEData)
    t = float(obj.PlateThickness.Value)
    margin = float(obj.OutlineMargin.Value)
    opening = float(obj.SwitchOpening.Value)
    lip = float(obj.ClipLipThickness.Value)
    relief = float(obj.ClipReliefWidth.Value)
    clip_span = float(obj.ClipReliefSpan.Value)
    if not all(math.isfinite(v) for v in (t, margin, opening, lip, relief, clip_span)):
        raise ValueError('All dimensions must be finite')
    if not (t > 0 and margin >= 0 and 10 <= opening <= 17):
        raise ValueError('Thickness/margin/opening values outside accepted limits')
    if obj.UndersideClipRelief and not (0 < lip < t):
        raise ValueError('Clip lip must be greater than 0 and less than plate thickness')
    if relief <= 0 or clip_span <= 0:
        raise ValueError('Clip relief dimensions must be positive')

    # Envelopes are identical to the successful four-switch print.
    faces = [_key_polygon(key, margin) for key in keys]
    outline = str(getattr(obj, 'OutlineShape', 'Follow layout'))
    if outline == 'Rectangle':
        # Use the same expanded envelopes as the default outline, including rotation.
        left = min(face.BoundBox.XMin for face in faces)
        bottom = min(face.BoundBox.YMin for face in faces)
        right = max(face.BoundBox.XMax for face in faces)
        top = max(face.BoundBox.YMax for face in faces)
        base = Part.makeBox(right - left, top - bottom, t, Vector(left, bottom, 0))
    elif outline == 'Follow layout':
        envelope = faces[0].multiFuse(faces[1:]) if len(faces) > 1 else faces[0]
        envelope = _refine(envelope)
        base = envelope.extrude(Vector(0, 0, t))
    else:
        raise ValueError('Unknown outline shape: %s' % outline)

    cutters = []
    for key in keys:
        x, y, w, h, angle, rx, ry, label = key
        cx, cy = x + w / 2.0, y + h / 2.0
        # Full-depth standard MX aperture, nominal 14 x 14 mm.
        cutters.append(_rotated_box(cx, cy, opening, opening,
                                    -0.2, t + 0.4, key))
        if obj.UndersideClipRelief:
            # Keep SAME +/-Y clip-side geometry as the proven plate.
            # The extensions start where the through-hole ends.
            step = opening / 2.0 + relief / 2.0
            for sign in (-1, 1):
                cutters.append(_rotated_box(cx, cy + sign * step / PITCH,
                                            clip_span, relief, -0.1,
                                            t - lip + 0.1, key))
    tool = Part.makeCompound(cutters)
    result = _refine(base.cut(tool))
    if result.isNull() or result.Volume <= 0:
        raise ValueError('Boolean operation produced an empty plate')
    if len(result.Solids) != 1:
        raise ValueError('Expected one connected plate, got %d solids. Increase margin.' % len(result.Solids))
    if not result.isValid():
        raise ValueError('Generated BREP is invalid')

    bounds = result.BoundBox
    dx, dy = alignment_offset(
        (bounds.XMin, bounds.YMin, bounds.XMax, bounds.YMax),
        str(getattr(obj, 'PlacementReference', 'Keep layout coordinates')))
    if dx or dy or bounds.ZMin:
        transform = App.Placement(Vector(dx, dy, -bounds.ZMin), App.Rotation()).toMatrix()
        result = result.transformGeometry(transform)
    # Keep manual object Placement independent of the generated local alignment.
    placement = obj.Placement
    obj.Shape = result
    obj.Placement = placement
    obj.KeyCount = len(keys)
    obj.VolumeMM3 = result.Volume
    obj.SolidCount = len(result.Solids)
    obj.GenerationStatus = 'OK - %d keys, %d solid' % (len(keys), len(result.Solids))


