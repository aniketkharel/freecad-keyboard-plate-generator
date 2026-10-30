import unittest
from keyboard_plate.kle import parse_kle
from keyboard_plate.preview import layout_preview


class PreviewTests(unittest.TestCase):
    def test_sample_dimensions(self):
        keys = parse_kle('[["A","B"],["C","D"]]')
        envelopes, holes, bounds = layout_preview(keys, 5, 14)
        self.assertEqual(len(envelopes), 4)
        self.assertEqual(len(holes), 4)
        self.assertAlmostEqual(bounds[2] - bounds[0], 48.1)
        self.assertAlmostEqual(bounds[3] - bounds[1], 48.1)
        self.assertAlmostEqual(holes[0][1][0] - holes[0][0][0], 14)

    def test_rotated_rectangle(self):
        keys = parse_kle('[[{"r":90,"rx":2,"ry":3,"w":2},"A"]]')
        _, _, bounds = layout_preview(keys, 5, 14)
        self.assertAlmostEqual(bounds[2] - bounds[0], 29.05)
        self.assertAlmostEqual(bounds[3] - bounds[1], 48.1)

    def test_margin_expansion(self):
        keys = parse_kle('[["A"]]')
        _, _, a = layout_preview(keys, 5, 14)
        _, _, b = layout_preview(keys, 6, 14)
        self.assertAlmostEqual((b[2] - b[0]) - (a[2] - a[0]), 2)
