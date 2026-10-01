from sly import Parser
from ExprAstLexer import ExprAstLexer
from ast_nodes import * 
from tac_generator import *
from three_address_code import render_threeAddressCode 

class ExprAstParser(Parser):
    tokens = ExprAstLexer.tokens
    
    # A -> id = E
    @_('ID "=" E')
    def A(self, value):
        return Assign(Var(value[0]), value[2])

    # E -> E + T
    @_('E "+" T')
    def E(self, value):
        return BinOp('+', value[0], value[2])

    # E -> E - T
    @_('E "-" T')
    def E(self, value):
        return BinOp('-', value[0], value[2])

    # E -> T
    @_('T')
    def E(self, value):
        return value[0]

    # T -> T * F
    @_('T "*" F')
    def T(self, value):
        return BinOp('*', value[0], value[2])

    # T -> T / F
    @_('T "/" F')
    def T(self, value):
        return BinOp('/', value[0], value[2])

    # T -> T % F
    @_('T "%" F')
    def T(self, value):
        return BinOp('%', value[0], value[2])

    # T -> F
    @_('F')
    def T(self, value):
        return value[0]

    # F-> NUMBER
    @_('NUMBER')
    def F(self, value):
        return Num(value[0])

    # F-> ID
    @_('ID')
    def F(self, value):
        return Var(value[0])

    # F -> (E)
    @_('"(" E ")"')
    def F(self, value):
        return value[1]


lexer = ExprAstLexer()
parser = ExprAstParser()
inp = 'x=(a+b)*(c-d)+e'
result = parser.parse(lexer.tokenize(inp))
#print(pretty(result))
#to_dot(result)
insts = generate_for_statement(result)
tac = render_threeAddressCode(insts)
print(tac)

