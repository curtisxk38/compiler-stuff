# inline ASM in llvm ir

Learned from [here](http://llvm.org/docs/LangRef.html#inline-assembler-expressions)

## Syscall
```
%5 = call i32 asm sideeffect "movl $$0x00000000, %edi\0Amovl $$0x0000000a, %edx\0Amovl $$0, %eax\0Asyscall\0A", "=A,{si},~{dirflag},~{fpsr},~{flags}"(i8* %4)
```
`%5` - result

`call i32 asm sideffect` - returns i32, call inline assembly with sideeffect

`"movl ... "` - asm instructions

`(i8* %4)` - actual parameters for previous thing, will come back to it

`"=A ... "` - list of flags, needs explaining

`"=A"` - means result of assembly (what we're storing in %5) comes from rax

(actually does: A: Special case: allocates EAX first, then EDX, for a single operand (in 32-bit mode, a 64-bit integer operand will get split into two registers). It is not recommended to use this constraint, as in 64-bit mode, the 64-bit operand will get allocated only to RAX – if two 32-bit operands are needed, you’re better off splitting it yourself, before passing it to the asm statement.)

`{si}` - means we want to put something from llvm ir lang into si register specifically. What we put here will show up in the `(...` part

`~ ...` - everything that starts with ~ is a clobber constraint

`(i8* %4)` is consumed by the `{si}`, so thats how the address to buffer (%4) gets into si for the system call to work properly

## gcc

LLVM ir mostly follows gcc extended asm convention? according to llvm docs:

```
LLVM’s support for inline asm is modeled closely on the requirements of Clang’s GCC-compatible inline-asm support. Thus, the feature-set and the constraint and modifier codes listed here are similar or identical to those in GCC’s inline asm support. However, to be clear, the syntax of the template and constraint strings described here is not the same as the syntax accepted by GCC and Clang, and, while most constraint letters are passed through as-is by Clang, some get translated to other codes when converting from the C source to the LLVM assembly.
```

Info on gcc [here](https://gcc.gnu.org/onlinedocs/gcc/Extended-Asm.html)

