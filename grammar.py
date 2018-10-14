import json

class Grammar:
    def __init__(self, json_file):
        with open(json_file, "r") as f:
                self.grammar = json.load(f)

        self.rules = []
        for rule in self.grammar["rules"]:
        	self.rules.append(Rule(rule))

        self.start = self.grammar["start"]
        self.nonterm = self.grammar["nonterm"]
        self.term = self.grammar["term"]

    def all_symbols(self):
        return self.nonterm + self.term

class Rule:
	def __init__(self, json_rule):
		self.lhs = json_rule["L"]
		self.rhs = json_rule["R"]

	def __repr__(self):
		return "{} -> {}".format(self.left, self.right)