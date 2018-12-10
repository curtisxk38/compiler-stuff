import unittest

import ll1
import grammar


class TestLL1(unittest.TestCase):
    def test_ll1(self):
        g = grammar.Grammar(json_file="test_input/test2.cfg")
        expected = [
            [g.rules[0], g.rules[0], g.rules[0], g.rules[0], None],
            [g.rules[1], g.rules[1], g.rules[2], g.rules[2], g.rules[2]],
            [g.rules[3], g.rules[4], None, None, None],
            [None, None, g.rules[5], g.rules[6], None]
         ]
        self.assertEqual(ll1.construct_parse_table(g), expected)
