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
	def __init__(self, grammar_dict):
		self.lhs = grammar_dict["L"]
		self.rhs = grammar_dict["R"]

	def __repr__(self):
		return "{} -> {}".format(self.lhs, "".join(self.rhs))