from sys import argv
from collections import deque
import itertools

# Define some constants
EPSILON = None

reserved = {
    'null': 'NULL',
    'true': 'TRUE',
    'false': 'FALSE',
    'void': 'TVOID',
    'int': 'TINT',
    'string': 'TSTRING',
    'bool': 'TBOOL',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'return': 'RETURN',
    'new': 'NEW',
    'var': 'VAR',
    'global': 'GLOBAL'
}

literal_tokens = {
    # Symbols
    'LPAREN': '(',
    'RPAREN': ')',
    'LBRACKET': '[',
    'RBRACKET': ']',
    'LBRACE': '{',
    'RBRACE': '}',
    'SEMICOLON': ';',
    'COMMA': ',',
    # Operators
    'ASSIGN': '=',
    'PLUS': '+',
    'MINUS': '-',
    'STAR': '*',
    'LSHIFT': '<<',
    'RLSHIFT': '>>',
    'RASHIFT': '>>>',
    'LESS': '<',
    'LESSEQ': '<=',
    'GREAT': '>',
    'GREATEQ': '>=',
    'EQ': '==',
    'NEQ': '!=',
    'LAND': '&',
    'LOR': '|',
    'BAND': '[&]',
    'BOR': '[|]',
    'NOT': '!',
    'TILDE': '~',
}

class DFA:
    class State:
        id_iter = itertools.count()
        def __init__(self):
            self.id = next(self.id_iter)
            self.accepted = False
            self.token = None # String
            self.transition = {} # Key: char, Value: State
            
        def __hash__(self):
            return hash(self.id)
        
        def __eq__(self, other):
            return self.id == other.id

class NFA:
    class State:
        id_iter = itertools.count()
        
        def __init__(self):
            self.id = next(self.id_iter)
            self.accepted = False
            self.token = None # String
            self.transition = {} # Key: char, Value: set<State>
            self.precedence = 0
            
        def __eq__(self, other):
            return self.id == other.id
        
        def __hash__(self):
            return hash(self.id)
            
    @staticmethod
    def from_string(s):
        nfa = NFA()
        if s == '':
            return nfa
        del nfa.start.transition[EPSILON]
        state = nfa.start
        for c in s[:-1]:
            tmp_state = NFA.State()
            state.transition[c] = {tmp_state}
            state = tmp_state
        state.transition[s[-1]] = {nfa.end}
        return nfa
    
    @staticmethod
    def from_letter():
        nfa = NFA()
        del nfa.start.transition[EPSILON]
        for i in range(26):
            nfa.start.transition[chr(ord('a') + i)] = {nfa.end}
            nfa.start.transition[chr(ord('A') + i)] = {nfa.end}
        
        return nfa
    
    @staticmethod
    def from_digit():
        nfa = NFA()
        del nfa.start.transition[EPSILON]
        for i in range(10):
            nfa.start.transition[str(i)] = {nfa.end}
        return nfa
    
    @staticmethod
    def from_any_char():
        nfa = NFA()
        del nfa.start.transition[EPSILON]
        for i in range(128):
            nfa.start.transition[chr(i)] = {nfa.end}
        return nfa
    
    def concat(self, from_):
        if EPSILON in self.end.transition:
            self.end.transition[EPSILON].add(from_.start)
        else:
            self.end.transition[EPSILON] = {from_.start}
    
    def set_union(self, from_):
        if EPSILON in self.start.transition:
            self.start.transition[EPSILON].add(from_.start)
        else:
            self.start.transition[EPSILON] = {from_.start}
        if EPSILON in from_.end.transition:
            from_.end.transition[EPSILON].add(self.end)
        else:
            from_.end.transition[EPSILON] = {self.end}
    
    def kleene_star(self):
        # Allow zero occurrence
        if EPSILON in self.start.transition:
            self.start.transition[EPSILON].add(self.end)
        else:
            self.start.transition[EPSILON] = {self.end}
            
        if EPSILON in self.end.transition:
            self.end.transition[EPSILON].add(self.start)
        else:
            self.end.transition[EPSILON] = {self.start}
    
    def to_DFA(self):
        all_states = self.__iter_states()
        symbols = set()
        for state in all_states:
            for c in state.transition.keys():
                if c != EPSILON:
                    symbols.add(c)
        
        dfa = DFA()
        start_closure = self.__epsilon_closure(self.start)
        start = DFA.State()
        dfa.start = start
        states = [start]
        nfa_to_dfa = {frozenset(start_closure): start} # Frozen set for hashability
        queue = deque([frozenset(start_closure)]) # queue for processing
        while queue:
            S = queue.popleft()
            dfa_S = nfa_to_dfa[S]
            
            for i in symbols:
                T = self.__move(S, i)
                
                if T:
                    T = frozenset(self.__epsilon_closure(T))
                    if T not in nfa_to_dfa:
                        dfa_T = DFA.State()
                        nfa_to_dfa[T] = dfa_T
                        queue.append(T)
                        states.append(dfa_T)
                    else:
                        dfa_T = nfa_to_dfa[T]
                        
                    dfa_S.transition[i] = dfa_T
        
        for state in states:
            S = next(key for key, value in nfa_to_dfa.items() if value == state)
            accepted_states = [nfa_state for nfa_state in S if nfa_state.accepted]
            if accepted_states:
                state.accepted = True
                max_precedence_state = max(accepted_states, key=lambda state: state.precedence)
                state.token = max_precedence_state.token
        
        return dfa
                
        
    def set_token_class_for_end_state(self, token, precedence=0):
        self.end.accepted = True
        self.end.token = token
        self.end.precedence = precedence
            
    def __init__(self, c=EPSILON):
        self.start = self.State()
        self.end = self.State()
        self.start.transition[c] = {self.end}
    
    def __iter_states(self):
        states = [self.start]
        queue = deque([self.start])
        visited = {self.start}
        
        while queue:
            state = queue.popleft()
            for neighbors in state.transition.values():
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
                        states.append(neighbor)
        
        return states
    
    
    def __epsilon_closure(self, state):
        if type(state) == self.State:
            state = {state}
        
        closure = set(state)
        queue = deque(state)
        while queue:
            cur = queue.popleft()
            if EPSILON in cur.transition:
                for next_state in cur.transition[EPSILON]:
                    if next_state not in closure:
                        closure.add(next_state)
                        queue.append(next_state)
        return closure
        
    
    def __move(self, closure, c):
        result = set()
        for state in closure:
            if c in state.transition:
                result = result.union(state.transition[c])
        return result
        
        
class Scanner:
    def __init__(self):
        self.nfa = NFA()
        del self.nfa.start.transition[EPSILON]
        self.dfa = None
        
        for key, value in reserved.items():
            self.add_token(key, value)
        for key, value in literal_tokens.items():
            self.add_token(value, key)
        self.add_id_token('ID')
        self.add_int_token('INTLITERAL')
        self.add_str_token('STRINGLITERAL')
        self.add_comment_token('COMMENT')
        self.add_ignore_token('IGNORE')
        self.NFA_to_DFA()
        
    def scan(self, filename):
        with open(filename, 'r') as f:
            s = f.read()
        
        pos = 0
        while pos < len(s):
            state = self.dfa.start
            lexeme = ''
            last_accepting = None
            last_lexeme = ''
            last_pos = pos
            while pos < len(s) and s[pos] in state.transition:
                lexeme += s[pos]
                state = state.transition[s[pos]]
                if state.accepted:
                    last_accepting = state
                    last_lexeme = lexeme
                    last_pos = pos
                pos += 1
            if last_accepting:
                token = last_accepting.token
                if token not in ['COMMENT', 'IGNORE']:
                    print(f'{token} {last_lexeme}')
                pos = last_pos + 1
            else:
                print(f'Illegal Character {s[pos]}')
                break
    
    def add_token(self, s, token, precedence=100):
        nfa = NFA.from_string(s)
        nfa.set_token_class_for_end_state(token, precedence)
        self.nfa.set_union(nfa)
    
    def add_id_token(self, token, precedence=50):
        nfa1 = NFA.from_letter()
        nfa2 = NFA.from_letter()
        nfa2.set_union(NFA.from_digit())
        nfa2.set_union(NFA.from_string('_'))
        nfa2.kleene_star()
        nfa1.concat(nfa2)
        nfa2.set_token_class_for_end_state(token, precedence)
        self.nfa.set_union(nfa1)
    
    def add_int_token(self, token, precedence=50):
        nfa = NFA.from_digit()
        nfa.kleene_star()
        nfa.set_token_class_for_end_state(token, precedence)
        self.nfa.set_union(nfa)
        
    def add_str_token(self, token, precedence=50):
        nfa1 = NFA.from_string('"')
        nfa2 = NFA.from_any_char()
        del nfa2.start.transition['"']
        nfa2.kleene_star()
        end = NFA.State()
        nfa2.end.transition['"'] = {end}
        nfa2.end = end
        nfa2.set_token_class_for_end_state(token, precedence)
        nfa1.concat(nfa2)
        self.nfa.set_union(nfa1)
    
    def add_comment_token(self, token, precedence=0):
        nfa1 = NFA.from_string('/*')
        nfa2 = NFA.from_any_char()
        del nfa2.start.transition['*']
        nfa2.kleene_star()
        nfa_star = NFA.from_any_char()
        end = NFA.State()
        nfa2.start.transition['*'] = {nfa_star.start}
        nfa_star.start.transition['*'] = {nfa_star.start}
        nfa_star.end.transition[EPSILON] = {nfa2.start}
        nfa_star.start.transition['/'] = {end}
        nfa2.end = end
        nfa2.set_token_class_for_end_state(token, precedence)
        nfa1.concat(nfa2)
        self.nfa.set_union(nfa1)
        
    def add_ignore_token(self, token, precedence=0):
        ignore = ' \n\r\t'
        nfa = NFA()
        del nfa.start.transition[EPSILON]
        for c in ignore:
            nfa.start.transition[c] = {nfa.end}
        nfa.set_token_class_for_end_state(token, precedence)
        self.nfa.set_union(nfa)
        
    
    def NFA_to_DFA(self):
        self.dfa = self.nfa.to_DFA()
        
    def print_nfa(self):
        self.nfa.print()
        
    def print_dfa(self):
        self.dfa.print()
        
if len(argv) != 2:
    print('Usage: python3 scanner.py <input_file>')
    exit(1)
    
Scanner().scan(argv[1])