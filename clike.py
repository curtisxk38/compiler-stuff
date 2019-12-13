import sys

import scanner
import grammar
import lr_parse_common
import canonicallr1
import slr1
import first_follow
import visit
import gen_ir
import ast

scanner_rules = [
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
    scanner.SymbolRule("if", "if"),
    scanner.SymbolRule("else", "else"),
    scanner.SymbolRule("while", "while"),
    scanner.SymbolRule("input", "input"),
    
    scanner.SymbolRule("[ \t\n]", "whitespace", add_symbol=False)
]


def temp(rule, children):
    print("Children of statement list: {}".format(children))
    return children[0].add_child(children[1])
    

grammar_dict = {
    "start": "program",
    "nonterm": ["program", "statement_list", "statement", 
            "expression", "return_exp"],
    "term": ["int_type","right_paren","left_paren",
             "left_brace","right_brace","semi",
             "return","main","int_literal","plus","minus","times",
             "if","else","while","input"],
    "rules": [
        # main stuff
        [   
            "program",
            ["int_type", "main", "left_paren", 
                  "right_paren", "left_brace", 
                  "statement_list",
                  "right_brace"
            ]
        ],
        # statements
        [
            "statement_list",
            ["statement_list", "statement"],
            temp
            #lambda rule, children: children[0].add_child(children[1])
        ],
        [
            "statement_list",
            ["statement"],
            lambda rule, children: ast.ASTNode("statement_list", children)
        ],
        ###############

        ###############
        [
            "statement",
            ["return", "expression", "semi"],
            lambda rule, children: children[1]
        ],
        [
            "statement",
            ["if", "left_paren", "expression", "right_paren", "left_brace", "statement", "right_brace"],
            lambda rule, children: ast.ASTNode("if statement", [children[2], children[5]])
        ],

        ##################
        # expressions
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
            lambda rule, children: children[1]
        ],
        [
            "expression",
            ["input", "left_paren", "right_paren"],
            lambda rule, children: ast.ASTNode("input_exp", [])
        ]

    ],
    "assoc": {"plus":"left","minus":"left","times":"left",},
    "prec":{"times":1}
}

def main(fname):
    with open(fname, "r") as infile:
        tokens = scanner.scan(infile, scanner_rules)
    tokens.append(scanner.Symbol("$", "EOF", -1, -1, -1))
    #print(tokens)
    g = grammar.Grammar(grammar_dict)

    lr_parse_common.augment_grammar(g)

    for rule in g.rules:
        if rule.to_node is None:
            rule.to_node = lambda rule, children: ast.ASTNode(rule.lhs, children)
    
    #kernel = canonicallr1.LR1Item(g.rules[-1], 0, "$")
    kernel = slr1.LR0Item(g.rules[-1], 0)
    
    first_set = first_follow.get_first(g)
    follow = first_follow.get_follow(g, first_set)
    
    #dfa = lr_parse_common.make_dfa(g, canonicallr1.closure, kernel, first_set)
    dfa = lr_parse_common.make_dfa(g, slr1.closure, kernel, first_set)
    #print(dfa.generate_dot_file())

    #action, goto_table = canonicallr1.make_parse_table(dfa, follow, g)
    action, goto_table = slr1.make_parse_table(dfa, follow, g) 
    #print(action)
    #print(goto_table)

    ast_root = lr_parse_common.parse(dfa, action, goto_table, tokens, g)
    
    print(ast.gen_ast_digraph(ast_root))

    
    gen_code = gen_ir.CodeGenVisitor(ast_root)
    gen_code.accept()
    with open(fname + ".ll", "w") as outfile:
        outfile.write(gen_code.get_code())

if __name__ == "__main__":
    main(sys.argv[1])