

class ASTNode:
	def __init__(self, lexeme, num_children):
		self.lexeme = lexeme
		self.children = [None] * num_children
		self.parent = None

	def __repr__(self):
		if len(self.children) == 0:
			return self.lexeme
		else:
			return "{}: {}".format(self.lexeme, self.children)

	def for_digraph(self):
		return "{} - {}".format(self.lexeme, hex(id(self)))