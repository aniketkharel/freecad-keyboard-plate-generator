# Copyright (c) 2026 eco-ergo.com
# SPDX-License-Identifier: MIT
"""Persistent parametric FreeCAD feature and property schema."""
import traceback
import FreeCAD as App
from .geometry import _generate
from .kle import parse_kle
from .parameters import LENGTH_PARAMETERS, UNDERSIDE_CLIP_RELIEF


class KeyboardPlateProxy:
    def __init__(self, obj):
        obj.Proxy = self

    def execute(self, obj):
        try:
            _generate(obj)
        except Exception as e:
            obj.GenerationStatus = 'ERROR: ' + str(e)
            App.Console.PrintError('[Keyboard Plate] ' + traceback.format_exc() + '\n')
            # Preserve last valid shape if a property becomes temporarily invalid.

    def onDocumentRestored(self, obj):
        obj.Proxy = self


def _add_props(obj, data):
    def length(name, group, value, description):
        obj.addProperty('App::PropertyLength', name, group, description)
        setattr(obj, name, value)
    obj.addProperty('App::PropertyString', 'KLEData', '01 Layout',
                    'KLE Raw Data or Download JSON contents. Edit to regenerate.')
    obj.KLEData = data
    for name, label, group, default, description in LENGTH_PARAMETERS:
        length(name, group, default, description)
    obj.addProperty('App::PropertyBool', 'UndersideClipRelief', '03 Cherry MX',
                    'Create underside clearance at the two MX clip sides')
    obj.UndersideClipRelief = UNDERSIDE_CLIP_RELIEF
    obj.addProperty('App::PropertyInteger', 'KeyCount', '04 Result', 'Generated key count')
    obj.addProperty('App::PropertyString', 'GenerationStatus', '04 Result', 'Last generation status')
    obj.addProperty('App::PropertyFloat', 'VolumeMM3', '04 Result', 'Generated volume in mm^3')
    obj.addProperty('App::PropertyInteger', 'SolidCount', '04 Result', 'Connected solids in generated geometry')
    for name in ('KeyCount', 'GenerationStatus', 'VolumeMM3', 'SolidCount'):
        obj.setEditorMode(name, 1)


def create_plate(doc, data):
    keys = parse_kle(data)
    obj = doc.addObject('Part::FeaturePython', 'KeyboardPlate')
    obj.Label = 'MX Keyboard Plate (%d keys)' % len(keys)
    _add_props(obj, data)
    KeyboardPlateProxy(obj)
    if App.GuiUp:
        obj.ViewObject.Proxy = 0
    return obj
