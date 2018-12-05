import first_follow
import grammar

class DFA:
    def __init__(self, states, transitions):
        self.states = states
        self.transitions = transitions

    def generate_dot_file(self):
        digraph = "digraph G {\n"

        for transition in self.transitions:
            start, end, sym = transition
            start_str = self.gen_state_label(start)
            end_str = self.gen_state_label(end)
            digraph += "\t\"{}\" -> \"{}\" [ label = \"{}\" ];\n".format(start_str, end_str, sym)
        digraph += "}"
        return digraph

    def gen_state_label(self, state):
        label = ""
        for rule in state.dist_rules:
            label += "{}\\n".format(rule)
        return label


class State:
    def __init__(self, dist_rules):
        self.dist_rules = list(dist_rules)
        self.transitions = {}

    def __repr__(self):
        return str(self.dist_rules)

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
    start_items = closure(set([kernel]), g)
    


    lr0_items = set([tuple(start_items)])
    transitions = []

    while True:
        old_size = len(lr0_items)
        to_add = []
        for items in lr0_items:
            for sym in g.all_symbols():
                new_items = tuple(goto(items, sym, g))
                if len(new_items) > 0:
                    transitions.append((items, new_items, sym))
                    to_add.append(new_items)
        lr0_items.update(to_add)
        if old_size == len(lr0_items):
            break
    items_to_states = {}
    for items in lr0_items:
        if items not in items_to_states:
            items_to_states[items] = State(items)
    actual_transitions = []
    for transition in transitions:
        start, end, sym = transition
        start_state = items_to_states[start]
        end_state = items_to_states[end]
        # update each states' transitions
        start_state.transitions[sym] = end_state
        # also save transitions
        actual_t = [start_state, end_state, sym]
        if actual_t not in actual_transitions:
            actual_transitions.append(actual_t)

    states = [states for _, states in items_to_states.items()]
    return DFA(states, actual_transitions)

def make_parse_table(dfa,follow,grammar):
    action = [[]]
    goto = [[]]

def goto(dist_rules, sym, g):
    new_items = []
    for dist_rule in dist_rules:
        if dist_rule.dist_pos < len(dist_rule.rule.rhs):
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

    print(closure(set([DistRule(g.rules[0],0)]), g))


    dfa = make_dfa(first, follow, g)
    print(dfa.generate_dot_file())

if __name__ == "__main__":
    main()