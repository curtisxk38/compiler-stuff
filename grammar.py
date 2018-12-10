import json

class Grammar:
    def __init__(self, json_file=None, grammar_dict=None):
        if json_file is not None:
            with open(json_file, "r") as f:
                    grammar_dict = json.load(f)

        self.rules = []
        for rule in grammar_dict["rules"]:
        	self.rules.append(Rule(rule))

        self.start = grammar_dict["start"]
        self.nonterm = grammar_dict["nonterm"]
        self.term = grammar_dict["term"]

    def all_symbols(self):
        return self.nonterm + self.term

class Rule:
	def __init__(self, grammar_dict):
		self.lhs = grammar_dict["L"]
		self.rhs = grammar_dict["R"]

	def __repr__(self):
		return "{} -> {}".format(self.lhs, "".join(self.rhs))