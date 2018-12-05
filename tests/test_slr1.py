import unittest

import first_follow
import grammar
import slr1


class TestClosure(unittest.TestCase):
    def test_clos1(self):
    	g = grammar.Grammar("test3.cfg")

    	kernel = slr1.DistRule(g.rules[0],0)
    	closure = slr1.closure(kernel, g)

    	expected = set([kernel, slr1.DistRule(g.rules[1], 0), slr1.DistRule(g.rules[2], 0)])

    	self.assertEqual(closure, expected)