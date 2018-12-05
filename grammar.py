import json

class Grammar:
    def __init__(self, json_file):
        with open(json_file, "r") as f:
                json_grammar = json.load(f)

        self.rules = []
        for rule in json_grammar["rules"]:
        	self.rules.append(Rule(rule))

        self.start = json_grammar["start"]
        self.nonterm = json_grammar["nonterm"]
        self.term = json_grammar["term"]

    def all_symbols(self):
        return self.nonterm + self.term

class Rule:
	def __init__(self, json_rule):
		self.lhs = json_rule["L"]
		self.rhs = json_rule["R"]

	def __repr__(self):
		return "{} -> {}".format(self.lhs, self.rhs)