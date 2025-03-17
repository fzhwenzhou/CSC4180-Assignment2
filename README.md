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
Both of them would output the tokens (except comments, which would be discarded). 

The program for testing correctness is in `run_test.sh`. Simply execute:
```bash
sh run_test.sh
```
To test it. If everything is okay, the output should be:
```

```

## 2. Design of the Scanner
The scanner has two implementations. The first implementation: `lex.py`, adopts the existing PLY (Python-Lex-Yacc) tool to scan the source code. The second implementation: `scanner.py`, performs scanning by hand by firstly construct the NFA (Non-Deterministic Finite Autometa) from the regular expressions of the tokens, and use subset construction to convert the NFA into DFA (Deterministic Finite Autometa). Finally, the scanner will use the DFA to scan the source code.

For `lex.py`, I firstly defined all the tokens, and then defined the regular expressions for all the tokens. For reserved words, I firstly recognize them as identifiers, and check if they are in the reserved words map. If they are, then change the type to the reserved word token. Otherwise, keep the type to be "ID." After that, instantiate the lexer object with `lex.lex()`. Finally, read the file and input to the lexer, iterate through the lexer's iterator, and print the token types and token values. This is the most straight-forward way to implement it. 

For `scanner.py`, I firstly defined the reserved word map "reserved" and operator literal map "literal_tokens." Then I defined three classes: DFA, NFA, and Scanner. Both DFA and NFA class have a subclass named "State," storing the DFA/NFA states. Both of the states have the following member variables: id, the unique ID for the state initialized by `count` iterator in `itertools` library in Python, ensuring that different states have different and ascending IDs; accepted, a boolean variable, indicating if the state is an accepting state; token, a string variable, that f the state is an accepting state, this variable will store the token type; and transition, a map from character to state for DFA and a set of state for NFA. However, the state for NFA has an additional parameter: precedence, indicating the precedence for scanning if encountering the same character. Then, they both have two overloading operators: `__eq__` function, which overloads the `==` operator, compares the id of itself and others; `__hash__` function, which overloads the `hash` operator, hashes its own ID as the hash of its whole object. Since different states have different IDs, this is safe. 

There is no other method defined in DFA class, nor initializer. There are indeed some member variables for DFA, but there is no need to declare or define it in the initializer, as they will be defined in `to_DFA` function. This takes the advantage of the runtime variable definition of Python.

For NFA class, the initializer creates two member variables: start and end, initialized to new NFA states. Then, it will add the parameter `c` to the transition map of the start state, with its value to be end. This creates an initial transition. If no `c` is provided in the parameter, the transition would be `EPSILON` by default.

Some functions are defined to perform set operations, including `concat`, `set_union`, and `kleene_star`. For `concat`, it will add an epsilon transition from the end state of self to the start state of another. For `set_union`, it will add an epsilon transition from the start state of self to the start state of another, and add another epsilon transition from the end state of another to the end state of self. For `kleene_star`, it will add an epsilon transition from the start state to the end state, and add another epsilon transition from the end state to the start state. This will create a loop to itself.     

Some helper static methods are implemented for easier implementation in scanner. These are: `from_string`, `from_letter`, `from_digit`, and `from_any_char`. For the latter three functions, it will firstly delete the default EPSILON transition from the start to end. Then, it will iterate all the characters in the range (either letter or digit, or any character depending on the function name), and add it to the `start` transition dictionary with value being `end`. For `from_string`, it will iterate through the string, create a new state for each character, and set the transition of the prior character state to each, just like implementing a singly linked list. For the last character state, it will set the transition map to the end.

Other methods are related to states manipulation. `set_token_class_for_end_state` would set the token to be an accepted token, and set the token name and precedence. Private method `__iter_states` will perform BFS on the NFA and store all the states in a Python list. `__epsilon_closure` will compute the epsilon closure of a specific state by iterating all the states reachable by EPSILON transition from it, similar to the BFS algorithm but with specific seeking condition. `__move` function iterate through all the states in the closure, and union all the transition sets for a specific character. These functions takes full advantage of dynamic typing of Python, which allows types to be parameter types to be determined at runtime, to achieve function overloading for different types of parameters.

Finally, the `to_DFA` function converts itself to DFA and returns the generated minimized DFA. It uses the subset construction algorithm: start with the NFA's start state and compute its epsilon closure with the existing function as the DFA's initial state. Then, for each DFA state (a set of NFA states, converted to Python frozenset for hashability), and for each input symbol, compute the set of NFA states reachable by consuming that symbol, including their epsilon closures; this set becomes a new DFA state, with transitions added accordingly. A DFA state is accepting if it contains any NFA accepting state, inheriting the highest-precedence token. Repeat this process, generating new DFA states from unprocessed ones, until no new states are added, resulting in a DFA. Then the DFA calls its minimize function to minimize it. In the end, the function will return the newly generated DFA. For the detailed implementation of DFA minimization, see "7. Bonus" part.

Finally comes the scanner class. In this class, some functions including `add_token`, `add_id_token`, `add_int_token`, etc. are helpers to build the NFA for various tokens according to the regular expression. For `add_token`, it adds a literal token, so it only needs to be constructed with `from_string`, and set the token class, and then union the new NFA with the NFA member variable. For `add_id_token`, it starts with letters, so I used `from_letter` to construct the first NFA. Then, I construct the second NFA by performing set union on `from_letter`, `from_digit`, and `from_string('_')` to indicate that the following could be letter, digit, or underscore. Next, perform kleene star operation to the second NFA. Concat two NFAs, and then set token class. Finally, union it with the self NFA. For `add_int_token`, it is constructed by `from_digit` and then performing kleene star operation. For `add_str_token`, it will firstly create an NFA with `from_string('"')` indicating the double quote as the beginning, and create another NFA with `from_any_char`. Delete the original transition of double quotes, and perform kleene star. Set the transition to be the new end state. Finally, replace the original end state of the second NFA and concatenate two NFAs. For `add_comment_token`, it will firstly construct an NFA from string "/\*". Next, construct another NFA from any character and delete the premature transition of "\*". Then, perform kleene star to it. Next, create a new NFA state named "nfa_star" which is also from any character, and change the transition of star to itself. For other characters, it will transit to the second NFA state, and if it is "/" then set the transition to the new end. Set the end of the second NFA to the new end. Finally, concatenate the two NFAs. For ignore tokens, just iterate all the ignore characters ` \t\r\n` and add it to the start's transition table, pointing to the end. 

As for the initializer of Scanner, it will firstly construct a new NFA, and iterate through all the values in reserved word map and literal token map, and use `add_token` method to add them. Then call the rest functions to add other types of tokens to NFA. Finally, call `NFA_to_DFA` function to convert it to DFA.

Finally it comes to the scanning function. It takes a filename as the parameter, and read the whole file to a single string. It will set the initial position to 0. Then, a while loop will iterate through the whole string, and check the DFA for matching. If some transition exists, then advance the iterator. If one state is accepting, then update the last accepting variable, and set the last accepting position. If some character does not match, then add the token as the last accepting token if it is not comment or ignore. If last accepting is None which means that no last accepting token received, then print error. 

## 3. Why Choosing Regular Expression
Regular expressions are chosen for lexical specifications in lexers because they offer a concise and expressive way to define token patterns. Their simplicity and maintainability ensures that they can be easily generated and modified. In addition, regular expression can be transformed into finite autometa for efficiency. In addition, its unambiguity nature ensures precise matching. There are some other historical reasons for choosing regular expression rather than other equivalence, such as regular expressions are widely used in lex and programming language libraries. Therefore, it is out of the box in most tools. 


## 4. Why NFA is More Suitable for Regex
Because NFA can translate any regular expression without extra effort. That is, it is much easier to build an NFA than a DFA directly from a regular expression. For example, a regular expression like `(a|b)*abb` may have different paths when recognizing "a" as it can either return to the first state indicated by the kleene star or enter into the "abb" section. NFA uses a set of states to represent a transition, so it could store both of the states. DFA, on the other hand, can only store one state per transition, thus it needs extra efforts.

## 5. How to Recognize Longest Match
The scanner ensures the longest match by advancing through the DFA as long as valid transitions exist, consuming characters into lexeme while tracking the most recent accepting state with `last_accepting`, `last_lexeme`, and `last_pos`. When no further transitions are possible, it falls back to the last accepting state, emits the corresponding token, and updates the position to `last_pos + 1`. This approach guarantees that the lexer prefers the longest possible token (e.g., abc rather than ab) by exploring all possible matches before committing, as seen in the inner while loop `while pos < len(s) and s[pos] in state.transition`. 

The most precedent match is handled implicitly through the DFA’s construction, where precedence is typically encoded by prioritizing rules (e.g., reserved words over ID) during the conversion of regular expressions to the DFA. When a state is accepting, its token field reflects the highest-precedence rule, so `last_accepting.token` automatically selects the correct token. The scanner itself doesn’t explicitly resolve precedence conflicts but relies on the DFA to tag accepting states appropriately. 
## 6. Why Should We Convert NFA into DFA
If using NFA to scan the code, it needs to use DFS (Depth-first search) to search through all the possible pathes if one transition would result in more than one states. If one path does not match, it needs to use backtracking to return to the nearest branch, and perform search in another branch. This method not only adds complexity to the algorithm, and make the scanning time longer, but also add randomness to the running time as choosing different branches would result in different running time. Therefore, converting NFA to DFA would simplify the process. Moreover, DFA is much easier to be minimized, and the minimized DFA would give an extra efficiency.

## 7. Bonus
For bonus, I have implemented DFA minimization algorithm (table filling) and applied it in `to_DFA` function to generate a more efficient DFA. The brief idea is as follows:
1. Find all reachable states with BFS, and store the stataes into a set. Sort the set according to the states' id and turn it into a list.
2. Iterate through all the states, and union the alphabet set with all the transition keys.
3. Generate all p, q pairs in states by using combination function.
4. Iterate through all the pairs. If one state is accepting while another is not, add the pair to the table. Also, if both are accepted and the tokens are different, do the same.
5. If there is some pair that is not marked but any of the state of them through any alphabet transition is marked, mark it.
6. Separate them into equivalence classes. Iterate all the states in the states set. Pop any state, and put all the states that their pair is not in the table into the equivalence class. Perform set difference operation from the states to the equivalence class, and append the equivalence class to the list of the euivalence classes. Finally, build DFA from the equivalence classes by iterating all the equivalence class, and set each one to a new state, whose token is the token of any element in the class. Finally, convert the new state map into linked list by insertion operations. Then, the new DFA is minimized.