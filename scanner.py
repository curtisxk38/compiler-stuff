import sys
import re

class SymbolRule:
    def __init__(self, re, token_name, to_value=lambda _: -1, add_symbol=True):
        self.re = re
        self.token_name = token_name
        self.to_value = to_value
        self.add_symbol = add_symbol

class Symbol:
    def __init__(self, token, lexeme, value, line, col):
        self.token = token
        self.lexeme = lexeme
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return "{}<{}> at ({},{})".format(self.token, self.lexeme,self.line,self.col)

rules = [
    SymbolRule("def", "function def"), 
    SymbolRule("[a-zA-z]+", "id"),
    SymbolRule("[ \n]", "whitespace", add_symbol=False)
]


def scan(f_iter):
    """
    won't be able to scan tokens that are multiline tokens
    tok_map => map token_num (int) to a (str)
    """
    symbols = []

    for _line_num, line in enumerate(f_iter):
        line_num = _line_num + 1
        col_num = 1
        while len(line) > 0:
            # remember which regular expression matched the longest string
            max_match_len = 0
            max_symbol = None

            for rule in rules:
                m = re.match(rule.re, line)
                if m is not None:
                    lexeme = m.group()
                    if len(lexeme) > max_match_len:
                        max_match_len = len(lexeme)
                        symbol = None
                        if rule.add_symbol:
                            symbol = Symbol(rule.token_name, lexeme, rule.to_value(lexeme), line_num, col_num)
                        max_symbol = symbol

            if max_match_len == 0:
                raise ValueError("No match found for ({}, {})".format(line_num, col_num))
            
            if max_symbol is not None:
                symbols.append(max_symbol)
            col_num += max_match_len
            line = line[max_match_len:]

    print(symbols)


def main():
    with open(sys.argv[1], "r") as infile:
        scan(infile)


if __name__ == "__main__":
    main()