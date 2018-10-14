import grammar

def base_follow(follow, first, g):
    # $ is in Follow(start symbol)
    follow[g.start].add("$")
    
    for rule in g.rules:
        # if B -> YXA, First(A) - "" is in Follow(X)
        if len(rule.rhs) > 1:
            last_sym = rule.rhs[-1]
            second_last_sym = rule.rhs[-2]
            # only proceed if second_last_sym is a non terminal
            #  if its terminal, we don't need a follow() set for it
            if second_last_sym in follow:
                # copy first[last_sym]
                first_last_sym = first[last_sym].copy()
                # remove "" from it
                try:
                    first_last_sym.remove("")
                except KeyError:
                    pass
                follow[second_last_sym].update(first_last_sym)


def get_follow(g, first):
    follow = {k: set() for k in g.nonterm}
    # cover base cases first
    base_follow(follow, first, g)

    
    while True:
        change_made = False
        for rule in g.rules:             
            # if B -> YXA, and "" in First(A), then Follow(B) is in Follow(A)
            if len(rule.rhs) > 1 and "" in first[rule.rhs[-1]]:
                second_last_sym = rule.rhs[-2]
                # only proceed if second_last_sym is a non terminal
                #  if its terminal, we don't need a follow() set for it
                if second_last_sym in follow:
                    # keep track of size of follow[second_last_sym] to see if changes are made
                    old_size = len(follow[second_last_sym])
                    # update follow
                    follow[second_last_sym].update(follow[rule.lhs])
                    # check if size is different, that means somethign was added to the follow set, 
                    #  and changes were made
                    if old_size != len(follow[second_last_sym]):
                        change_made = True
            
            # logically the same 'recursive' case as above, but have to handle this:
            #  if B -> X, then follow(B) in follow(A), because A becomes the empty string, so its like "" is in it
            #   we just don't represent RHS in our grammar as having [... "X", ""] that extra "" at the end
            # only relevant if X is a nonterminal
            elif len(rule.rhs) == 1 and rule.rhs[0] in follow:
                # keep track of size of follow set to see if changes are made
                old_size = len(follow[rule.rhs[0]])
                # update follow
                follow[rule.rhs[0]].update(follow[rule.lhs])
                # check if size is different, that means somethign was added to the follow set, 
                #  and changes were made
                if old_size != len(follow[rule.rhs[0]]):
                    change_made = True

        if not change_made:
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
            # find the first symbol in RHS of rule,
            #  where the symbol does not go to ""
            all_empty = True
            for sym in rule.rhs:
                if "" not in first[sym]:
                    first[rule.lhs].update(first[sym])
                    all_empty = False
                    break
            # also have add first(A) where A is the first symbol of RHS, regardless of whether "" in first(A)
            #  this is intuitive, because you could imagine RHS being ["", "A", ...], but the for loop won't handle
            #   this case because we didn't explicitly put the "" at the beginning of the RHS
            to_add = first[rule.rhs[0]].copy()
            # don't want to add the empty string "", if its in to_add because we should only
            #  add the empty string for in the special case where everything in RHS goes to "" (covered below)
            try:
                to_add.remove("")
            except KeyError:
                pass
            first[rule.lhs].update(to_add)

            # if all symbols in RHS of this rule go to ""
            #  then "" is in the first of LHS of this rule
            if all_empty:
                first[rule.lhs].add("")

            if old_size != len(first[rule.lhs]):
                change_made = True
        
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