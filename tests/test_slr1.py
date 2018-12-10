import unittest

import first_follow
import grammar
import slr1


class TestClosure(unittest.TestCase):
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
