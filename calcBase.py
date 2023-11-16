# -----------------------------------------------------------------------------
# calc.py
#
# Expressions arithmétiques sans variables
# -----------------------------------------------------------------------------

precedence = (
    ('left', 'AND', 'OR'),
    ('nonassoc', 'INF', 'SUP', 'INFEQ', 'SUPEQ'),
    ('left',       'PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('nonassoc', 'EQUALS'),
    ('nonassoc', 'LPAREN', 'RPAREN'),
    ('nonassoc', 'NAME'),
    ('nonassoc', 'NUMBER')
)

reserved = {
    'print' : 'PRINT'
}

tokens = [
    'NUMBER',       'MINUS',     
    'PLUS',         'TIMES',       'DIVIDE',
    'LPAREN',       'RPAREN',      'AND', 
    'OR',           'SEMI',        'NAME', 
    'EQUALS',       'INF',         'SUP', 
    'INFEQ',        'SUPEQ',
    'COMMENTLINE',  'COMMENTBLOCK','STRING'
] + list(reserved.values())

# Tokens
t_PLUS        = r'\+'
t_MINUS       = r'\-'
t_TIMES       = r'\*'
t_DIVIDE      = r'\/'
t_LPAREN      = r'\('
t_RPAREN      = r'\)'
t_AND         = r'\&'
t_OR          = r'\|'
t_SEMI        = r'\;'
t_EQUALS      = r'\='
t_INF         = r'\<'
t_SUP         = r'\>'
t_INFEQ       = r'\<\='
t_SUPEQ       = r'\>\='
t_COMMENTLINE = r'\/\/.+'
t_COMMENTBLOCK = r'\/\*[.\\n]*?\*\/' # NOTE: WE CAN'T TEST THIS YET
t_STRING       = r'\".*\"'

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'NAME')
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lex.lex()

names = {}

def p_block(p):
    '''block : block statement SEMI
             | statement SEMI
             | COMMENTLINE
             | COMMENTBLOCK'''
    
    if(len(p) == 4): # had to put the block on the left to execute the insturctions in the right order
        eval(p[2])
    else:
        eval(p[1])

def p_statement_assign(p):
    'statement : NAME EQUALS expression'
    p[0] = ('assign', p[1], p[3])

def p_statement_expr(p):
    'statement : PRINT LPAREN expression RPAREN'
    p[0] = ('print', p[3])

def p_statement_add_one(p):
    'statement : NAME PLUS PLUS'
    p[0] = ('incrementone', p[1])

def p_statement_sub_one(p):
    'statement : NAME MINUS MINUS'
    p[0] = ('decrementone', p[1])

def p_statement_add(p):
    'statement : NAME PLUS EQUALS expression'
    p[0] = ('increment', p[1], p[4])

def p_statement_sub(p):
    'statement : NAME MINUS EQUALS expression'
    p[0] = ('decrement', p[1], p[4])

def p_expression_binop_inf(p):
    'expression : expression INF expression'
    p[0] = ('smaller', p[1], p[3])

def p_expression_binop_sup(p):
    'expression : expression SUP expression'
    p[0] = ('greater', p[1], p[3])

def p_expression_binop_infeq(p):
    'expression : expression INFEQ expression'
    p[0] = ('smallerequal', p[1], p[3])

def p_expression_binop_supeq(p):
    'expression : expression SUPEQ expression'
    p[0] = ('greaterequal', p[1], p[3])

def p_expression_binop_plus(p):
    'expression : expression PLUS expression'
    # p[0] = p[1] + p[3]
    p[0] = ('add', p[1], p[3])

def p_expression_binop_times(p):
    'expression : expression TIMES expression'
    p[0] = ('multiply', p[1], p[3])

def p_expression_binop_divide_and_minus(p):
    '''expression : expression MINUS expression
				| expression DIVIDE expression'''

    if p[2] == '-': p[0] = ('substract', p[1], p[3])
    else : p[0] = ('divide', p[1], p[3])

def p_expression_binop_and(p):
    'expression : expression AND expression'
    p[0] = ('and', p[1], p[3])

def p_expression_binop_or(p):
    'expression : expression OR expression'
    p[0] = ('or', p[1], p[3])
    
def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]

def p_expression_string(p):
    'expression : STRING'
    p[0] = p[1].replace("\"", "")

def p_expression_name(p):
    'expression : NAME'
    p[0] = ('get', p[1])

def p_error(p):
    print("Syntax error at '%s'" % p.value)

def eval(t):
    if type(t) == int:
        return t

    if type(t) == tuple:
        if t[0] == 'add':
            return eval(t[1]) + eval(t[2])
        elif t[0] == 'substract':
            return eval(t[1]) - eval(t[2])
        elif t[0] == 'multiply':
            return eval(t[1]) * eval(t[2])
        elif t[0] == 'divide':
            if eval(t[2]) != 0:
                return eval(t[1]) / eval(t[2])
            else:
                print("Error: Division by zero")
                return None
        elif t[0] == 'print':
            print_value = eval(t[1])
            print("print >", print_value)
            return print_value
        elif t[0] == 'smaller':
            return eval(t[1]) < eval(t[2])
        elif t[0] == 'greater':
            return eval(t[1]) > eval(t[2])
        elif t[0] == 'smallerequal':
            return eval(t[1]) <= eval(t[2])
        elif t[0] == 'greaterequal':
            return eval(t[1]) >= eval(t[2])
        elif t[0] == 'and':
            return eval(t[1]) and eval(t[2])
        elif t[0] == 'or':
            return eval(t[1]) or eval(t[2])
        elif t[0] == 'assign':
            names[t[1]] = eval(t[2])
        elif t[0] == 'incrementone':
            names[t[1]] += 1
        elif t[0] == 'decrementone':
            names[t[1]] -= 1
        elif t[0] == 'increment':
            names[t[1]] += eval(t[2])
        elif t[0] == 'decrement':
            names[t[1]] -= eval(t[2])
        elif t[0] == 'get':
            return names.get(t[1])
    else:
        print("Unknown expression type:", t)
        return None

import ply.yacc as yacc
yacc.yacc()

s = input('calc > ')
yacc.parse(s)

    