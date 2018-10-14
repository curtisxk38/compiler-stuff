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
    stack = ["$", g.start]
    while True:
        try:
            first_sym = to_parse[0]
        except IndexError:
            break
        top = stack.pop()
        if top in g.nonterm:
            next_rule = parse_table[g.nonterm.index(top)][g.term.index(first_sym)]
        
            print(next_rule)
            
            for sym in next_rule.rhs[::-1]:
                if sym != "":
                    stack.append(sym)

        else:
            print("terminal: {}".format(top))
            to_parse = to_parse[1:]

def main():
    g = grammar.Grammar("test2.cfg")
    parse_table = construct_parse_table(g)
    parse(parse_table, g, "aab$")


if __name__ == "__main__":
    main()