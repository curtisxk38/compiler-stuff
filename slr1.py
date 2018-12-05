import first_follow
import grammar

class State:
    def __init__(self, dist_rules, transitions):
        self.dist_rules = dist_rules
        self.transitions = transitions

class DistRule:
    """
    class for a distinguished rule
    """
    def __init__(self,rule,dist_pos):
        self.rule = rule
        # an integer index, the dist_pos comes after rule.rhs[dist_pos - 1]
        #  and comes before rule.rhs[dist_pos]
        self.dist_pos = dist_pos

    def advance(self):
        # return new DistRule that is this DistRule
        #   with the distinguished marker advanced one spot
        return DistRule(self.rule, self.dist_pos+1)

    def __eq__(self, other):
        return self.rule == other.rule and self.dist_pos == other.dist_pos

    def __hash__(self):
        return hash((self.rule,self.dist_pos))

    def __repr__(self):
        rhs_with_dist = self.rule.rhs[:]
        rhs_with_dist.insert(self.dist_pos, ".")
        return "{} -> {}".format(self.rule.lhs, "".join(rhs_with_dist))

def make_dfa(first, follow, g):
    # augment grammar
    new_start = g.start + "'"
    old_start = g.start
    g.start = new_start
    g.nonterm.append(new_start)
    new_rule = grammar.Rule({"L":new_start, "R":[old_start]})
    g.rules.append(new_rule)

    kernel = DistRule(g.rules[0],0)
    
    
    dfa = [[]]
    
    return dfa

def make_parse_table(dfa,follow,grammar):
    action = [[]]
    goto = [[]]

def goto(dist_rules, sym, g):
    new_items = []
    for dist_rule in dist_rules:
        sym_after = dist_rule.rule.rhs[dist_rule.dist_pos]
        if sym_after == sym:
            new_items.append(dist_rule.advance())
    return closure(set(new_items), g)

def closure(closure_set, g):
    # modifies the closure_set parameter in place and returns it
    while True:
        # need to have a temporary list of things to add for next iteration
        #  because you can't modify a python set while you're iterating through it
        to_add = []
        old_size = len(closure_set)
        for dist_rule in closure_set:
            # if dist marker is not at the end of the rhs
            if dist_rule.dist_pos < len(dist_rule.rule.rhs):
                sym_after = dist_rule.rule.rhs[dist_rule.dist_pos]
                for rule in g.rules:
                    if rule.lhs == sym_after:
                        to_add.append(DistRule(rule, 0))
        # if we didn't add anything, we're done
        closure_set.update(to_add)
        if old_size == len(closure_set):
            break
    return closure_set

def main():
    g = grammar.Grammar("test3.cfg")
    first = first_follow.get_first(g)
    follow = first_follow.get_follow(g, first)

    print(closure(set([DistRule(g.rules[0],0), g])))


    dfa = make_dfa(first, follow, g)
    print(dfa)

if __name__ == "__main__":
    main()