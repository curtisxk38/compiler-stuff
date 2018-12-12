import unittest

import first_follow
import grammar
import slr1


class TestSLR1(unittest.TestCase):
    def test_clos1(self):
        g = grammar.Grammar(json_file="test_input/test3.cfg")


        kernel = slr1.DistRule(g.rules[0],0)
        closure = slr1.closure(set([kernel]), g)

        expected = set([kernel, slr1.DistRule(g.rules[1], 0), slr1.DistRule(g.rules[2], 0)])

        self.assertEqual(closure, expected)

    def test_goto1(self):
        g = grammar.Grammar(json_file="test_input/test3.cfg")
        kernel = slr1.DistRule(g.rules[0],0)
        closure = slr1.closure(set([kernel]), g)

        new_items = slr1.goto(closure, "(", g)

        expected = set([
            slr1.DistRule(g.rules[1],1),
            slr1.DistRule(g.rules[4],0),
            slr1.DistRule(g.rules[3],0),
            slr1.DistRule(g.rules[1],0),
            slr1.DistRule(g.rules[2],0),
            ])

        self.assertEqual(new_items, expected)

    def test_gen_table(self):
        g = grammar.Grammar(json_file="test_input/test4.cfg")
        slr1.augment_grammar(g)
        first = first_follow.get_first(g)
        follow = first_follow.get_follow(g, first)

        dfa = slr1.make_dfa(first, follow, g)

        with self.assertRaises(slr1.ShiftReduceError):
            action, goto_table = slr1.make_parse_table(dfa, follow, g)

