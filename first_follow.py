import grammar

def follow(g):
    pass

def base_first(first, g):
    for sym in first:
        # sym is a terminal, first(sym) = [sym]
        if sym in g.grammar["term"]:
            first[sym].append(sym)
        # sym is non terminal and sym -> "", so first[sym] has ""
        elif {"L":sym,"R":[""]} in g.grammar["rules"]:
            first[sym].append("")
def get_first(g):
    first = {k: [] for k in g.all_symbols()}
    # cover 2 base cases
    base_first(first, g)
    # 'recursive' step
    change_made = False
    while True:
        # iterate over rules in grammar
        for rule in g.grammar["rules"]:
            # find the first symbol in RHS of rule,
            #  where the symbol does not go to ""
            for sym in rule["R"]:
                if "" not in first[sym]:
                    first[rule["L"]].extend(first[sym])
                    break
        
        # do the 'recursive' step until no changes are made to any first sets        
        if not change_made:
            break

    return first

def main():
    g = grammar.Grammar("test.json")
    print(get_first(g))

if __name__ == "__main__":
    main()