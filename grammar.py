import json

class Grammar:
    def __init__(self, json_file):
        with open(json_file, "r") as f:
                self.grammar = json.load(f)

    def all_symbols(self):
        return self.grammar["nonterm"] + self.grammar["term"]
