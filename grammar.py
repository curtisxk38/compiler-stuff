import json

class Grammar:
    def __init__(self, grammar_dict):
        self.grammar_dict = grammar_dict
        self.rules = []
        for rule in grammar_dict["rules"]:
        	self.rules.append(Rule(rule))

        self.start = grammar_dict["start"]
        self.nonterm = grammar_dict["nonterm"]
        self.term = grammar_dict["term"]
        # add associativity and precedence
        if "prec" in grammar_dict:
            self.prec = grammar_dict["prec"]
        else:
            self.prec = {}
        if "assoc" in grammar_dict:
            self.assoc = grammar_dict["assoc"]
        else:
            self.assoc = {}

    def all_symbols(self):
        return self.nonterm + self.term

class Rule:
	def __init__(self, rule_def):
		self.lhs = rule_def[0]
		self.rhs = rule_def[1]

	def __repr__(self):
		return "{} -> {}".format(self.lhs, "".join(self.rhs))

def make_dummy_grammar(fname):
    with open(fname, "r") as f:
        grammar_dict = json.load(f)
    g = Grammar(grammar_dict=grammar_dict)
    return g