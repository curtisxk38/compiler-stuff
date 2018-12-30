import sys

import scanner
import grammar
import lr_parse_common
import slr1
import first_follow
import visit
import gen_ir
import ast

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
    "nonterm": ["program", "expression", "return_exp"],
    "term": ["int_type","right_paren","left_paren",
             "left_brace","right_brace","semi",
             "return","main","int_literal","plus","minus","times"],
    "rules": [
        [   
            "program",
            ["int_type", "main", "left_paren", 
                  "right_paren", "left_brace", "return",
                  "return_exp", "semi", "right_brace"
            ]
        ],
        [
            "return_exp",
            ["expression"],
            lambda rule, children: ast.ASTNode("return_exp", children)
        ],
        [
            "expression",
            ["int_literal"],
            lambda rule, children: ast.ASTNode("int_literal", [], symbol=children[0])
        ],
        [
            "expression",
            ["expression", "plus", "expression"],
            lambda rule, children: ast.ASTNode("plus_exp", [children[0], children[2]])
        ],
        [
            "expression",
            ["expression", "minus", "expression"],
            lambda rule, children: ast.ASTNode("minus_exp", [children[0], children[2]])
        ],
        [
            "expression",
            ["expression", "times", "expression"],
            lambda rule, children: ast.ASTNode("times_exp", [children[0], children[2]])
        ],
        [
            "expression",
            ["left_paren", "expression", "right_paren"],
            lambda rule, children: children[0]
        ],

    ],
    "assoc": {"plus":"left","minus":"left","times":"left",},
    "prec":{"times":1}
}

def main(fname):
    with open(fname, "r") as infile:
        tokens = scanner.scan(infile, rules)
    tokens.append(scanner.Symbol("$", "EOF", -1, -1, -1))
    #print(tokens)
    g = grammar.Grammar(grammar_dict)

    lr_parse_common.augment_grammar(g)

    for rule in g.rules:
        if rule.to_node is None:
            rule.to_node = lambda rule, children: ast.ASTNode(rule.lhs, children)
    
    kernel = slr1.LR0Item(g.rules[-1], 0)
    first_set = first_follow.get_first(g)
    follow = first_follow.get_follow(g, first_set)
    dfa = lr_parse_common.make_dfa(g, slr1.closure, kernel, first_set)
    action, goto_table = slr1.make_parse_table(dfa, follow, g)
    ast_root = lr_parse_common.parse(dfa, action, goto_table, tokens, g)
    print(ast.gen_ast_digraph(ast_root))
    gen_code = gen_ir.CodeGenVisitor(ast_root)
    gen_code.accept()
    print(gen_code.code)

if __name__ == "__main__":
    main(sys.argv[1])