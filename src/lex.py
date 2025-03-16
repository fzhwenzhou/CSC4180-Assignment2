from ply import lex
from sys import argv


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

tokens = [
    # Symbols
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'LBRACE',
    'RBRACE',
    'SEMICOLON',
    'COMMA',
    # Operators
    'ASSIGN',
    'PLUS',
    'MINUS',
    'STAR',
    'LSHIFT',
    'RLSHIFT',
    'RASHIFT',
    'LESS',
    'LESSEQ',
    'GREAT',
    'GREATEQ',
    'EQ',
    'NEQ',
    'LAND',
    'LOR',
    'BAND',
    'BOR',
    'NOT',
    'TILDE',
    # Others
    'INTLITERAL',
    'STRINGLITERAL',
    'ID'
] + list(reserved.values())


t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMICOLON = r';'
t_COMMA = r','

t_ASSIGN = r'='
t_PLUS = r'\+'
t_MINUS = r'\-'
t_STAR = r'\*'
t_LSHIFT = r'<<'
t_RLSHIFT = r'>>'
t_RASHIFT = r'>>>'
t_LESS = r'<'
t_LESSEQ = r'<='
t_GREAT = r'>'
t_GREATEQ = r'>='
t_EQ = r'=='
t_NEQ = r'!='
t_LAND = r'&'
t_LOR = r'\|'
t_BAND = r'\[&\]'
t_BOR = r'\[\|\]'
t_NOT = r'!'
t_TILDE = r'~'

t_INTLITERAL = r'\d+'
t_STRINGLITERAL = r'"[^"]*"'

t_ignore_COMMENT = r'\/\*([^*]|\*+[^*/])*\*+\/'
t_ignore = ' \t\r\n'

def t_ID(t):
    r'[a-zA-Z_]\w*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_error(t):
    print(f'Illegal Character \'{t.value[0]}\'')
    exit(1)

lexer = lex.lex()

if len(argv) != 2:
    print('Usage: python3 lex.py <input_file>')
    exit(1)

with open(argv[1], 'r') as f:
    lexer.input(f.read())
    
for tok in lexer:
    print(f'{tok.type} {tok.value}')
