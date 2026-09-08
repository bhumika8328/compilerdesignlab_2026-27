"""
TinyCStr Level 1 -- AST to Three-Address Code (triple form) generator.


This walks a Function' statement AST and builds a
TripleProgram (see three_address_code.py).
with triples, an intermediate result's "name" is just
whatever index TripleProgram.append() gives it, so there's nothing to
allocate.
"""
from ast_nodes import Num, Var, Assign, Print, BinOp
from three_address_code import TripleTAC, BinOpTriple, AssignTriple, PrintTriple
from three_address_code import TripleTAC

class TACGenerator:
    def __init__(self):
        self.program = TripleTAC()

    def generate(self, function):
        """
        Provided -- the entry point. Walks function.getStatementsAstList()
        in order and returns the finished TripleTAC. You should not
        need to change this method; implement gen_stmt() and gen_expr()
        below instead.
        """
        for stmt in function.getStatementsAstList():
            self.gen_stmt(stmt)
        return self.program

    def gen_stmt(self, stmt):
        if isinstance(stmt, Assign):
              operand = self.gen_expr(stmt.expr)
              self.program.append(AssignTriple(stmt.var.name, operand))

        if isinstance(stmt, Print):
              operand = self.gen_expr(stmt.expr)
              self.program.append(PrintTriple(operand))

    
        

    def gen_expr(self, node):
        if isinstance(node, Num):
            return str(node.value)
                                

        if isinstance(node, Var):
            return node.name
                            

        if isinstance(node, BinOp):
            left  = self.gen_expr(node.left)
            right = self.gen_expr(node.right)
            return self.program.append(BinOpTriple(node.op, left, right))
              # append() sets the index and returns a ready TripleRef
              # for you -- that's the whole reason to use it here instead
              # of constructing BinOpTriple and a TripleRef separately.
   


        """Note the order: fully resolve both operands (which may themselves
        recursively append triples for nested BinOps) BEFORE appending
        this node's own triple -- otherwise triples come out numbered in
        the wrong order and later TripleRefs point at the wrong thing.
        """
