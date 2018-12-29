import unittest

import first_follow
import grammar
import slr1
import lr_parse_common


class TestSLR1(unittest.TestCase):
    def test_clos1(self):
        g = grammar.make_dummy_grammar("test_input/test3.cfg")


        kernel = slr1.LR0Item(g.rules[0],0)
        closure = slr1.closure(set([kernel]), g, None)

        expected = set([kernel, slr1.LR0Item(g.rules[1], 0), slr1.LR0Item(g.rules[2], 0)])

        self.assertEqual(closure, expected)

    def test_goto1(self):
        g = grammar.make_dummy_grammar("test_input/test3.cfg")
        kernel = slr1.LR0Item(g.rules[0],0)
        items = slr1.closure(set([kernel]), g, None)

        new_items = lr_parse_common.goto(slr1.closure, items, "(", g, None)

        expected = set([
            slr1.LR0Item(g.rules[1],1),
            slr1.LR0Item(g.rules[4],0),
            slr1.LR0Item(g.rules[3],0),
            slr1.LR0Item(g.rules[1],0),
            slr1.LR0Item(g.rules[2],0),
            ])

        self.assertEqual(new_items, expected)

    def test_make_table(self):
        g = grammar.make_dummy_grammar("test_input/test3.cfg")
        lr_parse_common.augment_grammar(g)
        first = first_follow.get_first(g)
        follow = first_follow.get_follow(g, first)

        kernel = slr1.LR0Item(g.rules[-1], 0)
        dfa = lr_parse_common.make_dfa(g, slr1.closure, kernel, first)

        action, goto_table = slr1.make_parse_table(dfa, follow, g)
        
        expected_action = [
            ['s3', 's4', None, None],
            [None, None, None, 'accept'],
            [None, None, None, 'r0'],
            ['r2', 'r2', 'r2', 'r2'],
            ['s3', 's4', None, None],
            ['s3', 's4', 'r4', None],
            [None, None, 's8', None],
            [None, None, 'r3', None],
            ['r1', 'r1', 'r1', 'r1']
        ]

        self.assertEqual(expected_action, action)

        expected_goto = [
            [1, 2, None, None],
            [None, None, None, None],
            [None, None, None, None],
            [None, None, None, None],
            [None, 5, 6, None],
            [None, 5, 7, None],
            [None, None, None, None],
            [None, None, None, None],
            [None, None, None, None]
        ]

        self.assertEqual(expected_goto, goto_table)


    def test_not_slr1_grammar(self):
        g = grammar.make_dummy_grammar("test_input/test4.cfg")
        lr_parse_common.augment_grammar(g)
        first = first_follow.get_first(g)
        follow = first_follow.get_follow(g, first)

        kernel = slr1.LR0Item(g.rules[-1], 0)
        dfa = lr_parse_common.make_dfa(g, slr1.closure, kernel, first)

        with self.assertRaises(lr_parse_common.ShiftReduceError):
            action, goto_table = slr1.make_parse_table(dfa, follow, g)

