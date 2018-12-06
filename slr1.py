import first_follow
import grammar

class DFA:
    def __init__(self, states, transitions, start_state):
        self.states = states
        self.transitions = transitions
        self.start_state = start_state

    def generate_dot_file(self):
        digraph = "digraph G {\n"
        # edge from nowhere to start state
        digraph += "\t\"\" [shape=none];\n"
        digraph += "\t\"\" -> \"{}\";\n".format(self.gen_state_label(self.start_state))

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
    def __init__(self, dist_rules, is_start):
        self.dist_rules = list(dist_rules)
        self.transitions = {}
        self.is_start = is_start

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

    kernel = DistRule(g.rules[-1],0)
    start_items = closure(set([kernel]), g)
    start_items = tuple(start_items)
    
    lr0_items = set([start_items])
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
            is_start = items == start_items
            items_to_states[items] = State(items, is_start)
    
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

    states = []
    start_state = None
    for _, state in items_to_states.items():
        states.append(state)
        if state.is_start:
            start_state = state
    return DFA(states, actual_transitions, start_state)

def construction_table_error(table, index, col_index, new_rule):
    print("Tried to put {} where {} already exists".format(new_rule, table[index][col_index]))
    raise ValueError("Not SLR1, multiple entries for action[{}][{}]".format(index, col_index))


def make_parse_table(dfa, follow, g):
    # + 1 to the number of terminals because we need $ in the table
    action = [[None] * (len(g.term)+1) for i in range(len(dfa.states))]
    goto_table = [[None] * len(g.nonterm) for i in range(len(dfa.states))]
    for index, state in enumerate(dfa.states):
        
        for sym, end_state in state.transitions.items():
            # create shift for action table
            if sym in g.term:
                col_index = g.term.index(sym)
                new_rule = "s{}".format(dfa.states.index(end_state))
                if action[index][col_index] is None:
                    action[index][col_index] = new_rule
                else:
                    construction_table_error(action, index, col_index, new_rule)
            # create goto entries
            else:
                # sym is nonterm
                col_index = g.nonterm.index(sym)
                goto_table[index][col_index] = dfa.states.index(end_state)
        
        for dist_rule in state.dist_rules:
            # create reduce for action table
            # if distinguished marker at very end of rhs
            if dist_rule.rule.lhs != g.start and dist_rule.dist_pos == len(dist_rule.rule.rhs):
                for sym in follow[dist_rule.rule.lhs]:
                    # if sym in follow(A), sym is a terminal
                    if sym == "$":
                        col_index = -1
                    else:
                        col_index = g.term.index(sym)
                    new_rule = "r{}".format(g.rules.index(dist_rule.rule))
                    if action[index][col_index] is None:
                        action[index][col_index] = new_rule
                    else:
                        construction_table_error(action, index, col_index, new_rule)
            # create accept for action table
            # When we augmented the grammar, we added a new rule at the end of the rules list
            if dist_rule.dist_pos == len(dist_rule.rule.rhs) and dist_rule.rule == g.rules[-1]:
                # If dist_rule.rule is: S' -> S.
                #  action[index][$] = accept
                if action[index][-1] is None:
                    action[index][-1] = "accept"
                else:
                    construction_table_error(action, index, len(action[index])-1, "accept")
    return action, goto_table

def parse(start_state, action_table, goto_table, input_string, g):
    stack = [start_state]
    while True:
        current_state = stack[-1]
        try:
            sym = g.term.index(input_string[0])
        except ValueError:
            # sym is $
            sym = -1
        
        action = action_table[current_state][sym]
        
        if action == "accept":
            break
        elif action[0] == "s":
            # shift
            next_state = int(action[1])
            stack.append(next_state)
            # take sym out of input
            input_string = input_string[1:]
        elif action[0] == "r":
            reduce_rule = g.rules[int(action[1])]
            to_pop = len(reduce_rule.rhs)
            for i in range(to_pop):
                stack.pop()
            exposed_state = stack[-1]
            # symbol you reduce to
            lhs_symbol = g.nonterm.index(reduce_rule.lhs)
            next_state = goto_table[exposed_state][lhs_symbol]
            stack.append(next_state)
            print(reduce_rule)
        else:
            raise ValueError("No valid action for state {} and symbol {}".format(current_state, sym))

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

    dfa = make_dfa(first, follow, g)
    #print(dfa.generate_dot_file())
    action, goto_table = make_parse_table(dfa, follow, g)
    #print(action)
    #print(goto_table)

    start_state = dfa.states.index(dfa.start_state)
    parse(start_state, action, goto_table, "(a)$", g)

if __name__ == "__main__":
    main()