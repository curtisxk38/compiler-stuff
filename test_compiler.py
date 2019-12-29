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


def main(fname):
    with open(fname, "r") as infile:
        tokens = scanner.scan(infile, scanner_rules)
    tokens.append(scanner.Symbol("$", "EOF", -1, -1, -1))
    # print(tokens)
    import cgrammar2
    g = grammar.Grammar(cgrammar2.grammar)

    lr_parse_common.augment_grammar(g)

    for rule in g.rules:
        if rule.to_node is None:
            rule.to_node = lambda rule, children: ast.ASTNode(rule.lhs, children)

    kernel = slr1.LR0Item(g.rules[-1], 0)

    first_set = first_follow.get_first(g)
    follow = first_follow.get_follow(g, first_set)

    dfa = lr_parse_common.make_dfa(g, slr1.closure, kernel, first_set)
    print(dfa.generate_dot_file())

    action, goto_table = slr1.make_parse_table(dfa, follow, g)
    # print(action)
    # print(goto_table)

    ast_root = lr_parse_common.parse(dfa, action, goto_table, tokens, g)

    print(ast.gen_ast_digraph(ast_root))

    gen_code = gen_ir.CodeGenVisitor(ast_root)
    gen_code.accept()
    with open(fname + ".ll", "w") as outfile:
        outfile.write(gen_code.get_code())


if __name__ == "__main__":
    main(sys.argv[1])
