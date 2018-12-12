import sys

import scanner
import grammar
import slr1

rules = [
    scanner.SymbolRule("int", "int_type"), 
    scanner.SymbolRule("\(", "left_paren"),
    scanner.SymbolRule("\)", "right_paren"),
    scanner.SymbolRule("{", "left_brace"),
    scanner.SymbolRule("}", "right_brace"),
    scanner.SymbolRule(";", "semi"),
    scanner.SymbolRule("return", "return"),
    scanner.SymbolRule("main", "main"),
    scanner.SymbolRule("([1-9][0-9]*)|0", "int_literal", to_value=lambda i: int(i)),
    scanner.SymbolRule("\+", "plus"),
    scanner.SymbolRule("-", "minus"),
    scanner.SymbolRule("\*", "times"),
    scanner.SymbolRule("[ \t\n]", "whitespace", add_symbol=False)
]

grammar_dict = {
    "start": "program",
    "nonterm": ["program", "expression"],
    "term": ["int_type","right_paren","left_paren",
             "left_brace","right_brace","semi",
             "return","main","int_literal","plus","minus","times"],
    "rules": [
        {
            "L": "program",
            "R": ["int_type", "main", "left_paren", 
                  "right_paren", "left_brace", "return",
                  "expression", "semi", "right_brace"]
        },
        {
            "L": "expression",
            "R": ["int_literal"]
        },
        {
            "L": "expression",
            "R": ["expression", "plus", "expression"]
        },
        {
            "L": "expression",
            "R": ["expression", "minus", "expression"]
        },
        {
            "L": "expression",
            "R": ["expression", "times", "expression"]
        },
        {
            "L": "expression",
            "R": ["left_paren", "expression", "right_paren"]
        },

    ]
}

def main(fname):
    with open(fname, "r") as infile:
        tokens = scanner.scan(infile, rules)
    tokens.append(scanner.Symbol("$", "EOF", -1, -1, -1))
    #print(tokens)
    g = grammar.Grammar(grammar_dict=grammar_dict)
    ast = slr1.parse_input(g, tokens)
    print(ast.gen_ast_digraph())

if __name__ == "__main__":
    main(sys.argv[1])