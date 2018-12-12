import unittest

import scanner


class TestScanner(unittest.TestCase):
    def test_scanner1(self):
        rules = [
            scanner.SymbolRule("def", "function def"), 
            scanner.SymbolRule("[a-zA-z]+", "id"),
            scanner.SymbolRule("[ \n]", "whitespace", add_symbol=False)
        ]
        
        with open("test_input/scan.log", "r") as infile:
            symbols = scanner.scan(infile, rules)

        expected = [
            scanner.Symbol("function def", "def", -1, 1, 1),
            scanner.Symbol("id", "asdf", -1, 1, 5),
            scanner.Symbol("id", "popo", -1, 2, 1),
            scanner.Symbol("id", "asdf", -1, 2, 6),
            scanner.Symbol("function def", "def", -1, 2, 11),
            scanner.Symbol("id", "defdef", -1, 2, 15),
        ]
        self.assertEqual(symbols, expected)