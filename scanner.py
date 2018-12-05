import sys
import re

class SymbolRule:
    def __init__(self, re, to_value=lambda _: -1):
        self.re = re
        self.to_value = to_value

class Symbol:
    def __init__(self, token, lexeme, value, line, col):
        self.token = token
        self.lexeme = lexeme
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return "{}<{}> at ({},{})".format(self.token, self.lexeme,self.line,self.col)

rules = [SymbolRule("def"), SymbolRule("[a-zA-z]+")]


def scan(f_iter, tok_map=None):
    """
    won't be able to scan tokens that are multiline tokens
    tok_map => map token_num (int) to a (str)
    """
    symbols = []

    for line_num, line in enumerate(f_iter):
        col = 1
        while len(line) > 0:
            x = len(line)
            line = line.strip()
            col += x - len(line)

            max_match_len = 0
            max_match = None
            
            for token_num, rule in enumerate(rules):
                m = re.match(rule.re, line)
                if m is not None:
                    lexeme = m.group()
                    if tok_map is not None:
                        token = tok_map[token_num]
                    else:
                        token = token_num
                    if len(lexeme) > max_match_len:
                        max_match_len = len(lexeme)
                        max_match = (Symbol(token, lexeme, rule.to_value(lexeme), line_num, col), m)

            if max_match is None:
                raise ValueError("No match found for ({}, {})".format(line_num, col))
            
            symbol, m = max_match
            symbols.append(symbol)
            span = m.span()
            col += span[1]
            line = line[span[1]:]

    print(symbols)


def main():
    with open(sys.argv[1], "r") as infile:
        scan(infile, tok_map=["function_decl","identifier"])


if __name__ == "__main__":
    main()