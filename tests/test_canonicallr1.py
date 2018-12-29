import unittest

import first_follow
import grammar
import lr_parse_common
from canonicallr1 import closure, LR1Item


class TestCanonical(unittest.TestCase):
    def test_clos1(self):
        g = grammar.make_dummy_grammar("test_input/test5.cfg")
        lr_parse_common.augment_grammar(g)
        kernel = set()
        initial = LR1Item(g.rules[-1], 0, "$")
        kernel.add(initial)
        first_set = first_follow.get_first(g)
        closure(kernel, g, first_set)
        expected = set([initial, LR1Item(g.rules[0], 0, "$"), LR1Item(g.rules[1], 0, "d"),
                        LR1Item(g.rules[1], 0, "c"), LR1Item(g.rules[2], 0, "d"),
                        LR1Item(g.rules[2], 0, "c")])


        self.assertEqual(kernel, expected)


