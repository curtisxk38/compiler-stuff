import collections
from scanner import Symbol


class ASTNode:
    def __init__(self, node_type: str, children: list, symbol: Symbol = None):
        self.node_type = node_type
        self.children = children
        self.parent = None
        self.symbol = symbol
        for idx, child in enumerate(self.children):
            if isinstance(child, ASTNode):
                child.parent = self
            elif isinstance(child, Symbol):
                # this case only occurs if one of the rules has no to_node function
                #  then it uses the default one and adds all tokens in RHS of rule to children of AST
                # its a Symbol
                new_child = ASTNode(child.token, [], child)
                new_child.parent = self
                self.children[idx] = new_child
                print(new_child)
                raise NotImplementedError
            else:
                raise ValueError("unknown child type: {}".format(type(child)))

    def add_child(self, new_child: 'ASTNode'):
        """
        in lambda exp for a node
        we want to add a new child to this node 
        and return a reference to this node

        this method is used for list type rules:
            ex: S -> Sa | a
            after 3 uses: want a AST like:
                S
              __|__
             |  |  |
             a  a  a
        """
        new_child.parent = self
        self.children.append(new_child)
        return self

    def __repr__(self):
        return f"ASTNode<self.node_type>"


def gen_ast_digraph(root: ASTNode):
    """
    generate diagram for ast rooted at this node
    """
    counter = 0
    node_to_id: Dict[ASTNode, int] = {}
    digraph = "digraph G {\n"
    unexamined: collections.deque = collections.deque()
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
