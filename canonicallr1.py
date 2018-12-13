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
    pass


def main():
    g = grammar.Grammar(json_file="test_input/test5.cfg")
    lr_parse_common.augment_grammar(g)
    kernel = LR1Item(g.rules[-1], 0, "$")
    first_set = first_follow.get_first(g)
    dfa = lr_parse_common.make_dfa(g, closure, kernel, first_set)
    print(dfa.generate_dot_file())

if __name__ == "__main__":
    main()