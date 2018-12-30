# Compiler stuff

## Compiling

```
python3 clike.py example.c
llc example.c.ll -march=x86-64 -o example.s
gcc -c example.s -o example.o
gcc example.o -o example.out
```

## Testing
```
python3 -m unittest tests/*.py
```