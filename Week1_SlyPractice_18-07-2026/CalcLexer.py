from sly import Lexer
class CalcLexer(Lexer):
<<<<<<< HEAD
    literals = {'+', '-', '*', '/', '%' , '^'}
=======
    literals = {'+', '-', '*', '/', '%', '^'}
>>>>>>> 24e5882cb7b6d4b0e01d4bd504151c34891700d8
    tokens   = { NUMBER }

    NUMBER = r'[0-9]+'

    def NUMBER(self, t):
        #print(' token is', t.type, t.value)
        t.value = int(t.value)
        return t

#to test run Lexer independently following code used
#inp = '2+3*5'
#lexer = CalcLexer()
# tokenize function which takes input string and returns tokens
#for token in lexer.tokenize(inp):
#    print( token.type, token.value,type(token.value))
