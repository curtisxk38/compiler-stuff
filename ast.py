import collections


class ASTNode:
    def __init__(self, node_type, children, symbol=None):
        self.node_type = node_type
        self.children = children
        self.parent = None
        self.symbol = symbol
        for idx, child in enumerate(self.children):
            if isinstance(child, ASTNode):
                child.parent = self
            else:
                # its a token_symbol
                new_child = ASTNode(child.token, [], child)
                new_child.parent = self
                self.children[idx] = new_child

    def __repr__(self):
       return self.node_type

def gen_ast_digraph(root):
    """
    generate diagram for ast rooted at this node
    """
    counter = 0
    node_to_id = {}
    digraph = "digraph G {\n"
    unexamined = collections.deque()
    unexamined.append(root)
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