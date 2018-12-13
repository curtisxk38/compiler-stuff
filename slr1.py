import first_follow
import grammar
import ast


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
        self.items = dist_rules
        self.transitions = {}
        self.is_start = is_start

    def __repr__(self):
        return str(self.dist_rules)

    def __eq__(self, other):
        return self.dist_rules == other.dist_rules

    def __hash__(self):
        return hash(tuple(self.items))

class LR0Item:
    """
    class for a distinguished rule
    """
    def __init__(self,rule,dist_pos):
        self.rule = rule
        # an integer index, the dist_pos comes after rule.rhs[dist_pos - 1]
        #  and comes before rule.rhs[dist_pos]
        self.dist_pos = dist_pos

    def advance(self):
        # return new LR0Item that is this LR0Item
        #   with the distinguished marker advanced one spot
        return LR0Item(self.rule, self.dist_pos+1)

    def __eq__(self, other):
        return self.rule == other.rule and self.dist_pos == other.dist_pos

    def __hash__(self):
        return hash((self.rule,self.dist_pos))

    def __repr__(self):
        rhs_with_dist = self.rule.rhs[:]
        rhs_with_dist.insert(self.dist_pos, ".")
        return "{} -> {}".format(self.rule.lhs, "".join(rhs_with_dist))

class Error(Exception):
    """
    Base class for exceptions in this module
    """
    pass

class ParseError(Error):
    """
    exception raised on parsing an input string that can't be made with the given grammar
    """
    pass

class ShiftReduceError(Error):
    """
    conflict in creating parse table: don't know whether to shift or reduce
    """
    pass

class ReduceReduceError(Error):
    """
    conflict in creating parse table: don't know which rule to reduce by
    """
    pass

def augment_grammar(g):
    """
    augment grammar g by adding new rule, S' -> S, where S was start symbol of g
    changes g in place
    """
    new_start = g.start + "'"
    old_start = g.start
    g.start = new_start
    g.nonterm.append(new_start)
    new_rule = grammar.Rule({"L":new_start, "R":[old_start]})
    g.rules.append(new_rule)

def make_dfa(first, follow, g):
    # the kernel is the new rule just added (by augmenting) with the dist marker at the beginning
    kernel = LR0Item(g.rules[-1], 0)
    start_state = State(closure(set([kernel]), g), True)

    states = [start_state]
    look_up = set([start_state])
    transitions = []

    while True:
        old_size = len(states)
        changes_made = False
        for state in states:
            for sym in g.all_symbols():
                new_items = goto(state.items, sym, g)
                if len(new_items) > 0:
                    new_state = State(new_items, False)
                    if new_state not in look_up:
                        look_up.add(new_state)
                        states.append(new_state)
                    # even if new_state is already in states,
                    #  this iteration through the sym for loop gives us a new transiiton
                    transitions.append([state, new_state, sym])
        if not changes_made:
            break

    # update each state so it has its own transitions
    for transition in transitions:
        source, dest, sym = transition
        source.transitions[sym] = dest

    return DFA(states, transitions, states[0])

def construction_table_error(table, index, col_index, new_rule):
    old_rule = table[index][col_index]
    print("Tried to put {} where {} already exists".format(new_rule, table[index][col_index]))
    if old_rule[0] == "r" and new_rule[0] == "r":
        raise ReduceReduceError("Reduce/Reduce error between states {} and {}".format(old_rule[1:], new_rule[1:]))
    if old_rule[0] == "s" and new_rule[0] == "r":
        raise ShiftReduceError("Shift/Reduce error: shift to state {}, reduce by rule {}".format(old_rule[1:], new_rule[1:]))
    if old_rule[0] == "r" and new_rule[0] == "s":
        raise ShiftReduceError("Shift/Reduce error: shift to state {}, reduce by rule {}".format(new_rule[1:], old_rule[1:]))    
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
                if goto_table[index][col_index] is None:
                    goto_table[index][col_index] = dfa.states.index(end_state)
                else:
                    raise ValueError("Goto already defined")
        
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

def parse(dfa, action_table, goto_table, tokens, g):
    start_state = dfa.states.index(dfa.start_state)
    parse_stack = [start_state]
    ast_stack = []
    while True:
        current_state = parse_stack[-1]
        token_symbol = tokens[0]
        try:
            sym = g.term.index(token_symbol.token)
        except ValueError:
            # sym is $
            sym = -1
        action = action_table[current_state][sym]
        
        if action is None:
            raise ParseError("No valid action for state {} and symbol {}".format(dfa.states[current_state], g.term[sym]))
        elif action == "accept":
            break
        elif action[0] == "s":
            # shift
            next_state = int(action[1:])
            parse_stack.append(next_state)
            # take sym out of input
            tokens = tokens[1:]
            # build ast
            ast_stack.append(ast.ASTNode(g.term[sym], 0))
        elif action[0] == "r":
            reduce_rule = g.rules[int(action[1])]
            print(reduce_rule)

            reduce_len = len(reduce_rule.rhs)
            # new AST node
            new_node = ast.ASTNode(reduce_rule.lhs, reduce_len)
            for i in range(reduce_len - 1, -1, -1):
                parse_stack.pop()
                child = ast_stack.pop()
                child.parent = new_node
                new_node.children[i] = child
            ast_stack.append(new_node)

            exposed_state = parse_stack[-1]
            # symbol you reduce to
            lhs_symbol = g.nonterm.index(reduce_rule.lhs)
            next_state = goto_table[exposed_state][lhs_symbol]
            parse_stack.append(next_state)
    return ast_stack[0]
            
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
                        to_add.append(LR0Item(rule, 0))
        # if we didn't add anything, we're done
        closure_set.update(to_add)
        if old_size == len(closure_set):
            break
    return closure_set

def parse_input(g, tokens):
    augment_grammar(g)
    first = first_follow.get_first(g)
    follow = first_follow.get_follow(g, first)

    dfa = make_dfa(first, follow, g)
    #print(dfa.generate_dot_file())
    action, goto_table = make_parse_table(dfa, follow, g)
    #print(action)
    #print(goto_table)

    ast = parse(dfa, action, goto_table, tokens, g)

    return ast

def main():
    import scanner
    g = grammar.Grammar(json_file="test_input/test3.cfg")
    augment_grammar(g)
    first = first_follow.get_first(g)
    follow = first_follow.get_follow(g, first)

    dfa = make_dfa(first, follow, g)
    print(dfa.generate_dot_file())
    action, goto_table = make_parse_table(dfa, follow, g)
    print(action)
    print(goto_table)

    tokens = scanner.dummy_tokenize("(a(a((a))))$")
    ast = parse(dfa, action, goto_table, tokens, g)
    #print(ast.gen_ast_digraph())

if __name__ == "__main__":
    main()