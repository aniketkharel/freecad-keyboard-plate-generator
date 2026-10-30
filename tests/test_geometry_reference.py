"""Guard the tested construction without requiring a FreeCAD installation."""
import ast
from pathlib import Path
import unittest


class MechanicalReferenceTests(unittest.TestCase):
    def test_coordinate_and_cutter_functions_unchanged(self):
        original = ast.parse(Path('reference/plate_generator_v0_2.FCMacro').read_text(encoding='utf-8'))
        current = ast.parse(Path('keyboard_plate/geometry.py').read_text(encoding='utf-8'))
        for name in ('_pt', '_key_polygon', '_rotated_box'):
            before = next(n for n in original.body if isinstance(n, ast.FunctionDef) and n.name == name)
            after = next(n for n in current.body if isinstance(n, ast.FunctionDef) and n.name == name)
            self.assertEqual(ast.dump(before), ast.dump(after), name)

    def test_entire_cutter_loop_unchanged(self):
        def cutter_loop(path):
            tree = ast.parse(Path(path).read_text(encoding='utf-8'))
            generate = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_generate')
            return next(n for n in generate.body if isinstance(n, ast.For))
        self.assertEqual(ast.dump(cutter_loop('reference/plate_generator_v0_2.FCMacro')),
                         ast.dump(cutter_loop('keyboard_plate/geometry.py')))

    def test_property_defaults_unchanged(self):
        from keyboard_plate.parameters import LENGTH_PARAMETERS, UNDERSIDE_CLIP_RELIEF
        tree = ast.parse(Path('reference/plate_generator_v0_2.FCMacro').read_text(encoding='utf-8'))
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_add_props')
        original = {n.args[0].value: n.args[2].value for n in ast.walk(function)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'length'}
        self.assertEqual(original, {p[0]: p[3] for p in LENGTH_PARAMETERS})
        self.assertIs(UNDERSIDE_CLIP_RELIEF, True)
