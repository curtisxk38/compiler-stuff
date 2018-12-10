import collections


class ASTNode:
    def __init__(self, node_type, num_children, symbol=None):
        self.node_type = node_type
        self.children = [None] * num_children
        self.parent = None
        self.symbol = symbol

    def __repr__(self):
        if len(self.children) == 0:
            return self.node_type
        else:
            return "{}: {}".format(self.node_type, self.children)

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
                digraph += "\t{} [ label=\"{}\" ];\n".format(counter, look_at.node_type)
                counter += 1
            # for root
            if look_at.parent is None:
                digraph += "\t\"\" -> {};\n".format(node_to_id[look_at])
            else:
                digraph += "\t{} -> {};\n".format(node_to_id[look_at.parent], node_to_id[look_at])
            unexamined.extend(look_at.children)
        digraph += "}"
        return digraph