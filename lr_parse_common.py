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

def make_dfa(g, closure, kernel, first_set):
    start_state = State(closure(set([kernel]), g, first_set), True)

    states = [start_state]
    look_up = set([start_state])
    transitions = []

    while True:
        old_size = len(states)
        changes_made = False
        for state in states:
            for sym in g.all_symbols():
                new_items = goto(closure, state.items, sym, g, first_set)
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

def goto(closure, items, sym, g, first_set):
    new_items = []
    for item in items:
        if item.dist_pos < len(item.rule.rhs):
            sym_after = item.rule.rhs[item.dist_pos]
            if sym_after == sym:
                new_items.append(item.advance())
    return closure(set(new_items), g, first_set)



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
    