import collections


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

    def gen_ast_digraph(self):
        """
        generate diagram for ast rooted at this node
        """
        counter = 0
        node_to_id = {}
        digraph = "digraph G {\n"
        unexamined = collections.deque()
        unexamined.append(self)
        digraph += "\t\"\" [shape=none];\n"
        while len(unexamined) > 0:
            look_at = unexamined.popleft()
            if look_at not in node_to_id:
                node_to_id[look_at] = counter
                digraph += "\t{} [ label=\"{}\" ];\n".format(counter, look_at.lexeme)
                counter += 1
            # for root
            if look_at.parent is None:
                digraph += "\t\"\" -> {};\n".format(node_to_id[look_at])
            else:
                digraph += "\t{} -> {};\n".format(node_to_id[look_at.parent], node_to_id[look_at])
            unexamined.extend(look_at.children)
        digraph += "}"
        return digraph