import grammar

def base_follow(follow, first, g):
    # $ is in Follow(start symbol)
    follow[g.start].add("$")

    for rule in g.rules:
        # Let X -> Y1 Y2 ... Yj Yj+1 ... Yk
        # for 1 <= j < k
        #  Follow(Yj) contains First(Yj+1) - {""}
        if len(rule.rhs) > 1:
            for index, sym in enumerate(rule.rhs):
                if sym in follow and index + 1 < len(rule.rhs):
                    following_sym = rule.rhs[index + 1]
                    to_add = first[following_sym].copy()
                    # remove "" from it
                    try:
                        to_add.remove("")
                    except KeyError:
                        pass
                    follow[sym].update(to_add)

def get_follow(g, first):
    follow = {k: set() for k in g.nonterm}
    # cover base cases first
    base_follow(follow, first, g)

    changes_made = True
    while changes_made:
        changes_made = False
        for rule in g.rules:
            # Let X -> Y1 Y2 ... Yj Yj+1 ... Yk
            last_sym = rule.rhs[-1]
            if last_sym in follow:
                # Follow(Yk) contains Follow(X)
                old_len = len(follow[last_sym])
                follow[last_sym].update(follow[rule.lhs])
                if len(follow[last_sym]) > old_len:
                    changes_made = True

            rhs_reversed = rule.rhs[::-1]
            for index, sym in enumerate(rhs_reversed):
                # if sym is not Yk
                if index + 1 < len(rhs_reversed):
                    previous_sym = rhs_reversed[index+1]
                    if previous_sym in follow and "" in first[sym]:
                        old_len = len(follow[previous_sym])
                        follow[previous_sym].update(follow[sym])
                        if len(follow[previous_sym]) > old_len:
                            changes_made = True
                    else:
                        break
    return follow


def base_first(first, g):
    for sym in first:
        # sym is a terminal, first(sym) = [sym]
        if sym in g.term:
            first[sym].add(sym)
        # sym is non terminal and sym -> "", so first[sym] has ""
        elif {"L":sym,"R":[""]} in g.rules:
            first[sym].add("")

def get_first(g):
    first = {k: set() for k in g.all_symbols()}
    # cover 2 base cases
    base_first(first, g)
    # 'recursive' step
    while True:
        change_made = False
        # iterate over rules in grammar
        for rule in g.rules:
            # keep track of size of first[rule.lhs] to see if changes are made
            old_size = len(first[rule.lhs])
            
            # Let X -> Y1 Y2 Y3 ... Yk
            all_empty = True
            # Let Yj be the first symbol in RHS, such that First(Yj) does not contain ""
            # First(X) contains First(Yi) - {""} for all Yi, i <= j
            for sym in rule.rhs:
                if "" not in first[sym]:
                    first[rule.lhs].update(first[sym])
                    all_empty = False
                    break
                else:
                    to_add = first[sym].copy()
                    try:
                        to_add.remove("")
                    except KeyError:
                        pass
                    first[rule.lhs].update(to_add)
            # If First(Y1), First(Y2) ... First(Yk) all contain ""
            #  then First(X) contains "" 
            if all_empty:
                first[rule.lhs].add("")

            if old_size != len(first[rule.lhs]):
                change_made = True
        
        # do the 'recursive' step until no changes are made to any first sets        
        if not change_made:
            break

    return first

def main():
    g = grammar.Grammar(json_file="test.json")
    first = get_first(g)
    print(first)
    follow = get_follow(g, first)
    print(follow)

if __name__ == "__main__":
    main()