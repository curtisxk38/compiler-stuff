import sys

import scanner
import grammar
import lr_parse_common
import slr1
import first_follow

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

    ],
    "assoc": {"plus":"left","minus":"left","times":"left",},
    "prec":{"times":1}
}

def main(fname):
    with open(fname, "r") as infile:
        tokens = scanner.scan(infile, rules)
    tokens.append(scanner.Symbol("$", "EOF", -1, -1, -1))
    #print(tokens)
    g = grammar.Grammar(grammar_dict=grammar_dict)

    lr_parse_common.augment_grammar(g)
    kernel = slr1.LR0Item(g.rules[-1], 0)
    first_set = first_follow.get_first(g)
    follow = first_follow.get_follow(g, first_set)
    dfa = lr_parse_common.make_dfa(g, slr1.closure, kernel, first_set)
    action, goto_table = slr1.make_parse_table(dfa, follow, g)
    ast = lr_parse_common.parse(dfa, action, goto_table, tokens, g)
    print(ast.gen_ast_digraph())

if __name__ == "__main__":
    main(sys.argv[1])