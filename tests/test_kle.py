import unittest
from keyboard_plate.kle import parse_kle


class ParserTests(unittest.TestCase):
    def test_reference_four_switches(self):
        with open('4x4_kle.json', encoding='utf-8') as stream:
            keys = parse_kle(stream.read())
        self.assertEqual([(k[0], k[1]) for k in keys], [(0, 0), (1, 0), (0, 1), (1, 1)])

    def test_cluster_origin_persists_on_next_row(self):
        keys = parse_kle('[[{"r":30,"rx":3,"ry":2},"A"],["B"]]')
        self.assertEqual(keys[1][:2], (3, 3))
        self.assertEqual(keys[1][4:7], (30, 3, 2))

    def test_modifiers_accumulate_and_reset_after_key(self):
        keys = parse_kle('[[{"w":2},{"x":0.5},"A","B"]]')
        self.assertEqual(keys[0][:4], (0.5, 0, 2, 1))
        self.assertEqual(keys[1][:4], (2.5, 0, 1, 1))

    def test_column_stagger_and_decal(self):
        keys = parse_kle('[["A",{"y":0.25},"B",{"d":true},"art","C"]]')
        self.assertEqual([(k[0], k[1]) for k in keys], [(0, 0), (1, 0.25), (3, 0.25)])

    def test_raw_rows(self):
        self.assertEqual(len(parse_kle('["A"], ["B"],;')), 2)

    def test_invalid_numbers(self):
        for value in ('NaN', 'Infinity', 'true', '"2"'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_kle('[[{"x":%s},"A"]]' % value)

    def test_empty_or_bad_width(self):
        for source in ('[]', '[[{"w":0},"A"]]', '[42]'):
            with self.subTest(source=source), self.assertRaises(ValueError):
                parse_kle(source)


if __name__ == '__main__':
    unittest.main()
