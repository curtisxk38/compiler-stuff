        [
            "statement",
            ["if", "left_paren", "expression", "right_paren", "left_brace", "statement_list", "right_brace"],
            lambda rule, children: ast.ASTNode("if_statement", [children[2], children[5]])
        ],
        [
            "statement",
            ["if", "left_paren", "expression", "right_paren", "left_brace", "statement_list", "right_brace",
            "else", "left_brace", "statement_list", "right_brace"],
            lambda rule, children: ast.ASTNode("if_statement", [children[2], children[5], children[10]])
        ],
        [
            "statement",
            ["while", "left_paren", "expression", "right_paren", "left_brace", "statement_list", "right_brace"],
            lambda rule, children: ast.ASTNode("while_statement", [children[2], children[5]])
        ],