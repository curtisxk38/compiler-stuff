import visit

class CodeGenVisitor(visit.DFSVisitor):
    def __init__(self, ast):
        super().__init__(ast)
        self.code = ""
        self.reg_num = 1
        self.indent = "  "
        self.exp_stack = []

    def default_in_visit(self, node):
        # override
        pass

    def default_out_visit(self, node):
        # override
        pass

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
        self.add_line(self.indent + "%{} = load i32, i32* %{}, align 4".format(self.reg_num, self.reg_num - 1))
        self.exp_stack.append(self.reg_num)
        self.reg_num += 1

    def _out_plus_exp(self, node):
        op2 = self.exp_stack.pop()
        op1 = self.exp_stack.pop()
        self.add_line(self.indent + "%{} = add i32 %{}, %{}".format(self.reg_num, op1, op2))
        self.exp_stack.append(self.reg_num)
        self.reg_num += 1

    def _out_minus_exp(self, node):
        op2 = self.exp_stack.pop()
        op1 = self.exp_stack.pop()
        self.add_line(self.indent + "%{} = sub i32 %{}, %{}".format(self.reg_num, op1, op2))
        self.exp_stack.append(self.reg_num)
        self.reg_num += 1

    def _out_times_exp(self, node):
        op2 = self.exp_stack.pop()
        op1 = self.exp_stack.pop()
        self.add_line(self.indent + "%{} = mul i32 %{}, %{}".format(self.reg_num, op1, op2))
        self.exp_stack.append(self.reg_num)
        self.reg_num += 1

    def _out_return_exp(self, node):
        self.add_line(self.indent + "ret i32 %{}".format(self.reg_num - 1))

    def _out_input_exp(self, node):
        """
        define i32 @main() #0 {
          %1 = alloca [2 x i8], align 1
          %2 = getelementptr inbounds [2 x i8], [2 x i8]* %1, i32 0, i32 0
          %3 = call i32 asm sideeffect "movl $$0x00000000, %edi\0Amovl $$0x00000002, %edx\0Amovl $$0, %eax\0Asyscall\0A", "={ax},{si},~{dirflag},~{fpsr},~{flags}"(i8* %2)
          %4 = getelementptr inbounds [2 x i8], [2 x i8]* %1, i64 0, i64 0
          %5 = load i8, i8* %4, align 1
          %6 = sext i8 %5 to i32
          ret i32 %6
        }
        """
        self.add_line(self.indent + "%{} = alloca [2 x i8], align 1".format(self.reg_num))
        self.reg_num += 1
        self.add_line(self.indent + "%{} = getelementptr inbounds [2 x i8], [2 x i8]* %{}, i32 0, i32 0".format(self.reg_num, self.reg_num - 1))
        self.reg_num += 1
        self.add_line(self.indent + '%{} = call i32 asm sideeffect "movl $$0x00000000, %edi\\0Amovl $$0x00000002, %edx\\0Amovl $$0, %eax\\0Asyscall\\0A", "={{ax}},{{si}},~{{dirflag}},~{{fpsr}},~{{flags}}"(i8* %{})'.format(self.reg_num, self.reg_num - 1))
        self.reg_num += 1
        self.add_line(self.indent + "%{} = getelementptr inbounds [2 x i8], [2 x i8]* %{}, i64 0, i64 0".format(self.reg_num, self.reg_num - 3))
        self.reg_num += 1
        self.add_line(self.indent + "%{} = load i8, i8* %{}, align 1".format(self.reg_num, self.reg_num - 1))
        self.reg_num += 1
        self.add_line(self.indent + "%{} = sext i8 %{} to i32".format(self.reg_num, self.reg_num - 1))
        self.exp_stack.append(self.reg_num)
        self.reg_num += 1