import unittest

import first_follow
import grammar


class TestFirst(unittest.TestCase):

    def test_first1(self):
        expected = {'A': set(['b']), 'D': set(['', 'd']), 'E': set(['', 'e']),
         'b': set(['b']), 'd': set(['d']), 'e': set(['e']), '': set([''])}

        got = first_follow.get_first(grammar.Grammar("test.json"))

        # for some reason, doing self.assertEqual(got, expected) always fails,
        #  even though the following works
        equal = got == expected
        self.assertTrue(equal)

    def test_first2(self):
        expected = {'S': set(['c', 'b', 'd', 'a']), 'A': set(['c', 'b', 'd', 'a']),
         'B': set(['', 'a']), 'C': set(['', 'c']), 'a': set(['a']), 'b': set(['b']),
          'c': set(['c']), 'd': set(['d']), '': set([''])}

        got = first_follow.get_first(grammar.Grammar("test2.cfg"))

        equal = got == expected
        self.assertTrue(equal)

class TestFollow(unittest.TestCase):

    def test_follow1(self):
        expected = {'A': set('$'), 'D': set(['$', 'e']), 'E': set()}
        g = grammar.Grammar("test.json")
        first = first_follow.get_first(g)
        got = first_follow.get_follow(g, first)

        equal = expected == got
        self.assertTrue(equal)

    def test_follow2(self):
        expected = {'S': set('$'), 'A': set('$'), 'B': set('b'), 'C': set('d')}
        g = grammar.Grammar("test2.cfg")
        first = first_follow.get_first(g)
        got = first_follow.get_follow(g, first)

        equal = expected == got
        self.assertTrue(equal)