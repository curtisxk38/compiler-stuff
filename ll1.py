import first_follow
import grammar

def construct_parse_table(g):
    first = first_follow.get_first(g)
    follow = first_follow.get_follow(g, first)
    # len(term) columns, since we also need a column for $ but not one for ""
    parse_table = [[None for j in range(len(g.term))] for i in range(len(g.nonterm))]

    # for rule A -> a (a could be string of terms/nonterms)
    for rule in g.rules:
        row = g.nonterm.index(rule.lhs)
        first_set = first[rule.rhs[0]]
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


def main():
    g = grammar.Grammar("test2.cfg")
    parse_table = construct_parse_table(g)
    print([i for i in g.term if i != ""] + ["$"])
    for row in parse_table:
        print(row)


if __name__ == "__main__":
    main()