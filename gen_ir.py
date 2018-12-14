import visit

class CodeGenVisitor(visit.DFSVisitor):
    def __init__(self, ast):
        super().__init__(ast)
        self.code = ""
        self.reg_num = 1
        self.indent = "  "

    def add_line(self, line):
        self.code += line + "\n"

    def _in_program(self, node):
        self.add_line("define i32 @main() #0 {")

    def _out_program(self, node):
        self.add_line("}")

    def _out_int_literal(self, node):
        self.add_line(self.indent + "%{} = alloca i32, align 4".format(self.reg_num))
        self.add_line(self.indent + "store i32 {}, i32* %{}".format(node.symbol.value, self.reg_num))
        self.reg_num += 1

    def _out_plus(self, node):
        self.add_line(self.indent + "%{} = add i32 %{}, %{}".format(self.reg_num, self.reg_num - 1, self.reg_num - 2))
        self.reg_num += 1

    def _out_minus(self, node):
        self.add_line(self.indent + "%{} = sub i32 %{}, %{}".format(self.reg_num, self.reg_num - 1, self.reg_num - 2))
        self.reg_num += 1

    def _out_times(self, node):
        self.add_line(self.indent + "%{} = mul i32 %{}, %{}".format(self.reg_num, self.reg_num - 1, self.reg_num - 2))
        self.reg_num += 1

    def __out_return(self, node):
        self.add_line(self.indent + "ret i32 %{}".format(self.reg_num - 1))