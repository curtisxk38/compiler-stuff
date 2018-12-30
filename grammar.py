import json
import collections
import ast


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
        # to_node is a function that returns a node in the AST
        #  when this rule is used to reduce by
        # NOTE: to_node is of type <function> not <bound method>, so it won't have access to 
        #  the special self parameter
        #  to_node should take two parameters, an explicit reference to the Rule its a member of,
        #   and a list of children
        try:
            self.to_node = rule_def[2]
        except IndexError:
            self.to_node = None

    def __repr__(self):
        return "{} -> {}".format(self.lhs, "".join(self.rhs))

def make_dummy_grammar(fname):
    with open(fname, "r") as f:
        grammar_dict = json.load(f)
    g = Grammar(grammar_dict=grammar_dict)
    for rule in g.rules:
        rule.to_node = lambda rule, children: ast.ASTNode(rule.lhs, children)
    return g