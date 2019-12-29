import ast

def temp(rule, children):
    print(children)
    return children[0].add_child(children[1])


grammar = {
    "start": "program",
    "nonterm": ["program", "statement_list", "statement",
                "expression", "return_exp"],
    "term": ["int_type", "right_paren", "left_paren",
             "left_brace", "right_brace", "semi",
             "return", "main", "int_literal", "plus", "minus", "times",
             "if", "else", "while", "input"],
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
        ],
    ],
    "assoc": {"plus": "left", "minus": "left", "times": "left", },
    "prec": {"times": 1}
}