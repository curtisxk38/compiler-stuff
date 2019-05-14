# Compiler stuff

## Compiling

```
python3 clike.py example.cl
llc example.cl.ll -march=x86-64 -o example.s
gcc -c example.s -o example.o
gcc example.o -o example.out
```

## Testing
```
python3 -m unittest tests/*.py
```