import unittest

import first_follow
import grammar
import slr1
from canonicallr1 import closure, LR1Item


class TestCanonical(unittest.TestCase):
    def test_clos1(self):
        g = grammar.Grammar(json_file="test_input/test5.cfg")
        slr1.augment_grammar(g)
        kernel = set()
        initial = LR1Item(g.rules[-1], 0, "$")
        kernel.add(initial)
        first_set = first_follow.get_first(g)
        closure(kernel, g, first_set)
        expected = set([initial, LR1Item(g.rules[0], 0, "$"), LR1Item(g.rules[1], 0, "d"),
                        LR1Item(g.rules[1], 0, "c"), LR1Item(g.rules[2], 0, "d"),
                        LR1Item(g.rules[2], 0, "c")])


        self.assertEqual(kernel, expected)


