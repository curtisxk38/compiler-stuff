import first_follow
import grammar
import ast
import lr_parse_common


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
                    lr_parse_common.construction_table_error(action, index, col_index, new_rule)
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
                        lr_parse_common.handle_conflict(action, index, col_index, new_rule, g)
                        
            # create accept for action table
            # When we augmented the grammar, we added a new rule at the end of the rules list
            if dist_rule.dist_pos == len(dist_rule.rule.rhs) and dist_rule.rule == g.rules[-1]:
                # If dist_rule.rule is: S' -> S.
                #  action[index][$] = accept
                if action[index][-1] is None:
                    action[index][-1] = "accept"
                else:
                    lr_parse_common.construction_table_error(action, index, len(action[index])-1, "accept")
    return action, goto_table

def closure(closure_set, g, first_set):
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

def main():
    import scanner
    g = grammar.make_dummy_grammar("test_input/test3.cfg")
    lr_parse_common.augment_grammar(g)
    first = first_follow.get_first(g)
    follow = first_follow.get_follow(g, first)

    # the kernel is the new rule just added (by augmenting) with the dist marker at the beginning
    kernel = LR0Item(g.rules[-1], 0)
    dfa = lr_parse_common.make_dfa(g, closure, kernel, first)
    print(dfa.generate_dot_file())
    action, goto_table = make_parse_table(dfa, follow, g)
    print(action)
    print(goto_table)

    tokens = scanner.dummy_tokenize("(a(a((a))))$")
    ast_root = lr_parse_common.parse(dfa, action, goto_table, tokens, g)
    print(ast.gen_ast_digraph(ast_root))

if __name__ == "__main__":
    main()