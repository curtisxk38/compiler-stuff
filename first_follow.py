import grammar

def base_follow(follow, first, g):
    # $ is in Follow(start symbol)
    follow[g.grammar["start"]].add("$")
    
    for rule in g.grammar["rules"]:
        # if B -> YXA, First(A) - "" is in Follow(X)
        if len(rule["R"]) > 1:
            last_sym = rule["R"][-1]
            second_last_sym = rule["R"][-2]
            # copy first[last_sym]
            first_last_sym = first[last_sym].copy()
            # remove "" from it
            try:
                first_last_sym.remove("")
            except KeyError:
                pass
            follow[second_last_sym].update(first_last_sym)


def get_follow(g, first):
    follow = {k: set() for k in g.grammar["nonterm"]}
    # cover base cases first
    base_follow(follow, first, g)

    change_made = False
    while False:
        for rule in g.grammar["rules"]:
            # if B -> YXA, and "" in First(A), then Follow(B) is in Follow(A)
            if len(rule["R"]) > 1 and "" in first[rule["R"][-1]]:
                second_last_sym = rule["R"][-2]
                follow[second_last_sym].update(follow[rule["L"]])

        if not change_made:
            break

    return follow

def base_first(first, g):
    for sym in first:
        # sym is a terminal, first(sym) = [sym]
        if sym in g.grammar["term"]:
            first[sym].add(sym)
        # sym is non terminal and sym -> "", so first[sym] has ""
        elif {"L":sym,"R":[""]} in g.grammar["rules"]:
            first[sym].add("")

def get_first(g):
    first = {k: set() for k in g.all_symbols()}
    # cover 2 base cases
    base_first(first, g)
    # 'recursive' step
    change_made = False
    while True:
        # iterate over rules in grammar
        for rule in g.grammar["rules"]:
            # find the first symbol in RHS of rule,
            #  where the symbol does not go to ""
            all_empty = True
            for sym in rule["R"]:
                if "" not in first[sym]:
                    first[rule["L"]].update(first[sym])
                    all_empty = False
                    break
            # if all symbols in RHS of this rule go to ""
            #  then "" is in the first of LHS of this rule
            if all_empty:
                first[rule["L"]].add("")
        
        # do the 'recursive' step until no changes are made to any first sets        
        if not change_made:
            break

    return first

def main():
    g = grammar.Grammar("test.json")
    first = get_first(g)
    print(first)
    follow = get_follow(g, first)
    print(follow)

if __name__ == "__main__":
    main()