# Copyright (c) 2026 eco-ergo.com
# SPDX-License-Identifier: MIT
"""KLE JSON parsing independent of FreeCAD; coordinates remain in KLE units."""
import json
import math


def number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('KLE %s must be a finite number' % name)
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('KLE %s must be a finite number' % name)
    return value


def parse_kle(source):
    """Return physical keys as (x,y,width,height,rotation_deg,rot_x,rot_y,label).

    KLE row coordinates: each new row resets x to the cluster origin, advances y by 1.
    x/y property modifiers shift the next key's cursor. w/h are one-key defaults.
    The rotation origin (rx, ry) and angle (r) persist within KLE clusters.
    """
    source = source.lstrip('\ufeff').strip().rstrip(';').strip()
    if not source:
        raise ValueError('KLE data is empty')
    try:
        data = json.loads(source)
    except json.JSONDecodeError:
        data = json.loads('[' + source.rstrip(',') + ']')
    if not isinstance(data, list):
        raise ValueError('Expected KLE rows (an array of arrays)')
    keys = []
    cursor_y = -1.0
    angle = 0.0
    rx = 0.0
    ry = 0.0
    for row in data:
        if isinstance(row, dict):
            continue  # KLE keyboard metadata
        if not isinstance(row, list):
            raise ValueError('Each KLE row must be an array')
        cursor_x = rx
        cursor_y += 1.0
        width, height, decal = 1.0, 1.0, False
        for element in row:
            if isinstance(element, dict):
                # Rotation-cluster origin in KLE is absolute in keyboard units.
                if 'rx' in element:
                    rx = number(element['rx'], 'rx')
                    cursor_x = rx
                if 'ry' in element:
                    ry = number(element['ry'], 'ry')
                    cursor_y = ry
                if 'r' in element:
                    angle = number(element['r'], 'r')
                cursor_x += number(element.get('x', 0.0), 'x')
                cursor_y += number(element.get('y', 0.0), 'y')
                width = number(element.get('w', width), 'w')
                height = number(element.get('h', height), 'h')
                decal = bool(element.get('d', decal))
            elif isinstance(element, str):
                if not decal:
                    if width <= 0 or height <= 0:
                        raise ValueError('Key width and height must be positive')
                    keys.append((cursor_x, cursor_y, width, height,
                                 angle, rx, ry, element.split('\n')[0]))
                cursor_x += width
                width, height, decal = 1.0, 1.0, False
            else:
                raise ValueError('Unexpected KLE element: ' + str(element)[:80])
    if not keys:
        raise ValueError('No physical keys found in KLE data')
    return keys
