import first_follow
import grammar
import lr_parse_common

class LR1Item:
    def __init__(self, rule, dist_pos, look_ahead):
        self.rule = rule
        # an integer index, the dist_pos comes after rule.rhs[dist_pos - 1]
        #  and comes before rule.rhs[dist_pos]
        self.dist_pos = dist_pos
        # a terminal symbol that is the next input 
        self.look_ahead = look_ahead

    def advance(self):
         # return new LR1Item that is this LR1Item
         #   with the distinguished marker advanced one spot
         return LR1Item(self.rule, self.dist_pos + 1, self.look_ahead)

    def __eq__(self, other):
        return all([self.rule == other.rule, self.dist_pos == other.dist_pos,
            self.look_ahead == other.look_ahead])

    def __hash__(self):
        return hash((self.rule,self.dist_pos,self.look_ahead))

    def __repr__(self):
        rhs_with_dist = self.rule.rhs[:]
        rhs_with_dist.insert(self.dist_pos, ".")
        return "[{} -> {}, {}]".format(self.rule.lhs, "".join(rhs_with_dist), self.look_ahead)

def closure(closure_set, g, first_set):
    # modifies closure_set in place and returns it
    while True:
        to_add = []
        old_size = len(closure_set)

        for item in closure_set:
            if item.dist_pos < len(item.rule.rhs):
                # item = [A -> alpha . B beta, a]
                alpha = item.rule.rhs[:item.dist_pos]
                B = item.rule.rhs[item.dist_pos]
                beta = item.rule.rhs[item.dist_pos+1:]
                # for each terminal b in FIRST(beta a)
                #  add [B -> . gamma, b] if it isn't in closure_set already
                #  B -> gamma is any rule with B on the lhs
                firsts = first_follow.first_of_string(first_set, beta + [item.look_ahead])
                for b in firsts:
                    to_add.extend([LR1Item(rule, 0, b) for rule in g.rules if rule.lhs == B])

        closure_set.update(to_add)
        if len(closure_set) == old_size:
            # didn't add anything new this cycle
            break
    return closure_set

def make_parse_table(dfa, follow, g):
    # + 1 to the number of terminals because we need $ in the table
    action = [[None] * (len(g.term)+1) for i in range(len(dfa.states))]
    goto_table = [[None] * len(g.nonterm) for i in range(len(dfa.states))]

    for index, state in enumerate(dfa.states):
        for sym, end_state in state.transitions.items():
            # create shift in action table
            if sym in g.term:
                col_index = g.term.index(sym)
                new_rule = "s{}".format(dfa.states.index(end_state))
                if action[index][col_index] is None:
                    action[index][col_index] = new_rule
                else:
                    lr_parse_common.construction_table_error(action, index, col_index, new_rule)
            # create goto entries
            else:
                # sym is nonterm
                col_index = g.nonterm.index(sym)
                if goto_table[index][col_index] is None:
                    goto_table[index][col_index] = dfa.states.index(end_state)
                else:
                    raise ValueError("Goto already defined")
        for item in state.dist_rules:
            # create reduce in action table
            if item.rule.lhs != g.start and item.dist_pos == len(item.rule.rhs):
                if item.look_ahead == "$":
                    col_index = -1
                else:
                    col_index = g.term.index(item.look_ahead)
                new_rule = "r{}".format(g.rules.index(item.rule))
                if action[index][col_index] is None:
                    action[index][col_index] = new_rule
                else:
                    lr_parse_common.construction_table_error(action, index, col_index, new_rule)
            
            # create accept for action table
            # When we augmented the grammar, we added a new rule at the end of the rules list
            if item.dist_pos == len(item.rule.rhs) and item.rule == g.rules[-1]:
                # If item.rule is: S' -> S.
                #  action[index][$] = accept
                if action[index][-1] is None:
                    action[index][-1] = "accept"
                else:
                    lr_parse_common.construction_table_error(action, index, len(action[index])-1, "accept")
    return action, goto_table

def main():
    import scanner
    g = grammar.Grammar(json_file="test_input/test4.cfg")
    lr_parse_common.augment_grammar(g)
    kernel = LR1Item(g.rules[-1], 0, "$")
    first_set = first_follow.get_first(g)
    follow = first_follow.get_follow(g, first_set)
    dfa = lr_parse_common.make_dfa(g, closure, kernel, first_set)
    print(dfa.generate_dot_file())
    action, goto = make_parse_table(dfa, follow, g)

    tokens = scanner.dummy_tokenize("i=*i$")
    ast = lr_parse_common.parse(dfa, action, goto, tokens, g)
    print(ast.gen_ast_digraph())

if __name__ == "__main__":
    main()