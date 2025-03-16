# CSC4180 Assignment 2: Implement a Scanner for Oat v.1 Language

## Name: Fang Zihao, Student ID: 122090106

## 1. Usage
Before you run this program, ensure that you have the following environment installed on your machine:
- Python 3 (3.6 or above)

This project is totally cross-platform, so as long as you have a valid Python 3 installation, it should run without any issue.

To scan a program with PLY (Python-Lex-Yacc), simply execute:
```bash
python3 lex.py <input_file>
```

To scan a program with hand-written scanner, simply execute:
```bash
python3 scanner.py <input_file>
```
Both of them would output the tokens (except comments, which would be discarded). If the input is the same, the output of them should also be the same.

## 2. Design of the Scanner
The scanner has two implementations. The first implementation: `lex.py`, adopts the existing PLY (Python-Lex-Yacc) tool to scan the source code. The second implementation: `scanner.py`, performs scanning by hand by firstly construct the NFA (Non-Deterministic Finite Autometa) from the regular expressions of the tokens, and use subset construction to convert the NFA into DFA (Deterministic Finite Autometa). Finally, the scanner will use the DFA to scan the source code.

For `lex.py`, I firstly defined all the tokens, and then defined the regular expressions for all the tokens. For reserved words, I firstly recognize them as identifiers, and check if they are in the reserved words map. If they are, then change the type to the reserved word token. Otherwise, keep the type to be "ID." After that, instantiate the lexer object with `lex.lex()`. Finally, read the file and input to the lexer, iterate through the lexer's iterator, and print the token types and token values. This is the most straight-forward way to implement it. 

For `scanner.py`, I firstly defined the reserved word map "reserved" and operator literal map "literal_tokens." Then I defined three classes: DFA, NFA, and Scanner. Both DFA and NFA class have a subclass named "State," storing the DFA/NFA states. Both of the states have the following member variables: id, the unique ID for the state initialized by `count` iterator in `itertools` library in Python, ensuring that different states have different and ascending IDs; accepted, a boolean variable, indicating if the state is an accepting state; token, a string variable, that f the state is an accepting state, this variable will store the token type; and transition, a map from character to state for DFA and a set of state for NFA. However, the state for NFA has an additional parameter: precedence, indicating the precedence for scanning if encountering the same character. Then, they both have two overloading operators: `__eq__` function, which overloads the `==` operator, compares the id of itself and others; `__hash__` function, which overloads the `hash` operator, hashes its own ID as the hash of its whole object. Since different states have different IDs, this is safe. 

There is no other method defined in DFA class, nor initializer. There are indeed some member variables for DFA, but there is no need to declare or define it in the initializer, as they will be defined in `to_DFA` function. This takes the advantage of the runtime variable definition of Python.

For NFA class, the initializer creates two member variables: start and end, initialized to new NFA states. Then, it will add the parameter `c` to the transition map of the start state, with its value to be end. This creates an initial transition. If no `c` is provided in the parameter, the transition would be `EPSILON` by default.


