import first_follow
import grammar
import ast

def construct_parse_table(g):
    first = first_follow.get_first(g)
    follow = first_follow.get_follow(g, first)
    # len(term) columns, since we also need a column for $ but not one for ""
    parse_table = [[None for j in range(len(g.term))] for i in range(len(g.nonterm))]

    # for rule A -> a (a could be string of terms/nonterms)
    for rule in g.rules:
        row = g.nonterm.index(rule.lhs)
        first_set = []
        for idx, sym in enumerate(rule.rhs):
            if len(first_set) == 0:
                first_set.extend(first[sym])
            else:
                if "" in first[rule.rhs[idx - 1]]:
                    first_set.extend(first[sym])
        # For each term t in First(a) add A->a to M[A,t] (only if t != "")
        for term in first_set:
            col = g.term.index(term)
            if term != "":
                parse_table[row][col] = rule
            # If "" in First(a), for each terminal b in Follow(A),
            #  add A->a to M[A,b]
            else:
                follow_set = follow[rule.lhs]
                for sym in follow_set:
                    if sym == "$":
                        col = -1
                    else:
                        col = g.term.index(sym)
                    parse_table[row][col] = rule


    return parse_table

def parse(parse_table, g, to_parse):
    parse_stack = ["$", g.start]
    ast_stack = []
    while True:
        try:
            first_sym = to_parse[0]
        except IndexError:
            break
        top = parse_stack.pop()
        if top in g.nonterm:
            next_rule = parse_table[g.nonterm.index(top)][g.term.index(first_sym)]
        
            print(next_rule)
            # build AST
            ast_stack.append(ast.ASTNode(next_rule.lhs, len(next_rule.rhs)))
            
            for sym in next_rule.rhs[::-1]:
                parse_stack.append(sym)

        else:
            if top == "":
                top = "(empty string)"
            print("terminal: {}".format(top))
            to_parse = to_parse[1:]
            leaf = ast.ASTNode(top, 0)
            ast_stack.append(leaf)
            cleaning_ast = True
            # connect tree components
            while cleaning_ast and len(ast_stack) > 1:
                new_child = ast_stack.pop()
                parent = ast_stack.pop()
                used_new_child = False
                for idx, child in enumerate(parent.children):
                    if child is None:
                        if not used_new_child:
                            parent.children[idx] = new_child
                            new_child.parent = parent
                            used_new_child = True
                        else:
                            cleaning_ast = False
                            break # break out of for loop
                ast_stack.append(parent)
    return ast_stack[0]

def print_ast_digraph(root):
    digraph = "digraph G {\n"
    unexamined = [root]
    digraph += "\t\"\" [shape=none];\n"
    while len(unexamined) > 0:
        look_at = unexamined.pop()
        # for root
        if look_at.parent is None:
            digraph += "\t\"{}\" -> \"{}\";\n".format("", look_at.for_digraph())
        else:
            digraph += "\t\"{}\" -> \"{}\";\n".format(look_at.parent.for_digraph(), look_at.for_digraph())
        unexamined.extend(look_at.children)
    digraph += "}"
    return digraph

def main():
    g = grammar.Grammar("test2.cfg")
    parse_table = construct_parse_table(g)
    ast = parse(parse_table, g, "aab$")
    print(print_ast_digraph(ast))

if __name__ == "__main__":
    main()