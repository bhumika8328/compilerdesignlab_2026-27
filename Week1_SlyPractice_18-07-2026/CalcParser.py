from sly import Parser
from CalcLexer import CalcLexer

class CalcParser(Parser):
    tokens = CalcLexer.tokens
    literals = CalcLexer.literals

    # E -> E + T
    @_('E "+" T')
    def E(self, value):
        return value[0] + value[2]

    # E -> E - T
    @_('E "-" T')
    def E(self, value):
        return value[0]- value[2]

    # E -> T
    @_('T')
    def E(self, value):
        return value[0]

    # T -> T * F
    @_('T "*" F')
    def T(self, value):
        return value[0] * value[2]

    # T -> T / F
    @_('T "/" F')
    def T(self, value):
        return value[0] // value[2]

    # T -> T % F
    @_('T "%" F')
    def T(self, value):
        return value[0] % value[2]

    # T -> F
    @_('F')
    def T(self, value):
        return value[0]

    @_('NUMBER "^" F')
    def F(self, value):
        return value[0] ** value[2]

    @_('NUMBER')
    def F(self, value):
        return value[0]

lexer = CalcLexer()
parser = CalcParser()
inp = '1089-2^3^2*5'
result = parser.parse(lexer.tokenize(inp))
print(result)
