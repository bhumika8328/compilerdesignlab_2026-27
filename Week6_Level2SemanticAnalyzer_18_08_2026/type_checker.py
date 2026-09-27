from ast_nodes import (
    Const, Var, Assign, Print,
    BinOp, RelOp, Cast, Ternary
)

from SymbolTable import DataType
from type_rules import is_numeric, promote, SemanticError


class TypeChecker:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.errors = []

    def error(self, message, lineno):
        self.errors.append(
            SemanticError(message, lineno)
        )

    def check_const(self, node):
        return node, node.type

    def check_var(self, node):
        entry = self.symbol_table.getSymbol(node.name)

        if entry is None:
            self.error(
                f"undeclared variable '{node.name}'",
                node.lineno
            )

            # Fallback type so checking can continue
            return node, DataType.INT

        return node, entry.getDataType()

    def check_expr(self, node):
        if isinstance(node, Const):
            return self.check_const(node)

        if isinstance(node, Var):
            return self.check_var(node)

        if isinstance(node, BinOp):
            return self.check_binop(node)

        if isinstance(node, RelOp):
            return self.check_relop(node)

        if isinstance(node, Cast):
            return self.check_cast(node)

        if isinstance(node, Ternary):
            return self.check_ternary(node)

        return node, DataType.INT

    def check_binop(self, node):
        left_node, left_type = self.check_expr(node.left)
        right_node, right_type = self.check_expr(node.right)

        node.left = left_node
        node.right = right_node

        # Both operands must be numeric
        if not is_numeric(left_type) or not is_numeric(right_type):
            self.error(
                f"invalid operands to '{node.op}'",
                node.lineno
            )

            return node, DataType.INT

        # Find common numeric type
        result_type = promote(left_type, right_type)

        # Insert implicit cast if necessary
        if left_type != result_type:
            node.left = Cast(
                result_type,
                node.left,
                lineno=node.lineno
            )

        if right_type != result_type:
            node.right = Cast(
                result_type,
                node.right,
                lineno=node.lineno
            )

        return node, result_type

    def check_relop(self, node):
        left_node, left_type = self.check_expr(node.left)
        right_node, right_type = self.check_expr(node.right)

        node.left = left_node
        node.right = right_node

        if not is_numeric(left_type) or not is_numeric(right_type):
            self.error(
                f"invalid operands to '{node.op}'",
                node.lineno
            )

            return node, DataType.INT

        result_type = promote(left_type, right_type)

        if left_type != result_type:
            node.left = Cast(
                result_type,
                node.left,
                lineno=node.lineno
            )

        if right_type != result_type:
            node.right = Cast(
                result_type,
                node.right,
                lineno=node.lineno
            )

        # Relational expressions produce an integer result
        return node, DataType.INT

    def check_cast(self, node):
        expr_node, expr_type = self.check_expr(node.expr)
        node.expr = expr_node

        target_type = node.target_type

        # Numeric types can be explicitly converted
        if is_numeric(expr_type) and is_numeric(target_type):
            return node, target_type

        self.error(
            f"invalid cast to {target_type.name}",
            node.lineno
        )

        return node, target_type

    def check_ternary(self, node):
        cond_node, cond_type = self.check_expr(node.cond)
        then_node, then_type = self.check_expr(node.then_expr)
        else_node, else_type = self.check_expr(node.else_expr)

        node.cond = cond_node
        node.then_expr = then_node
        node.else_expr = else_node

        # Condition must be numeric
        if not is_numeric(cond_type):
            self.error(
                "invalid ternary condition",
                node.lineno
            )

        # Same type: nothing to convert
        if then_type == else_type:
            return node, then_type

        # Both numeric: promote them
        if is_numeric(then_type) and is_numeric(else_type):
            result_type = promote(then_type, else_type)

            if then_type != result_type:
                node.then_expr = Cast(
                    result_type,
                    node.then_expr,
                    lineno=node.lineno
                )

            if else_type != result_type:
                node.else_expr = Cast(
                    result_type,
                    node.else_expr,
                    lineno=node.lineno
                )

            return node, result_type

        # Incompatible branches
        self.error(
            "incompatible ternary expressions",
            node.lineno
        )

        return node, then_type

    def check_assign_stmt(self, node):
        # Check the left-hand variable
        var_node, var_type = self.check_var(node.var)
        node.var = var_node

        # Check right-hand expression
        expr_node, expr_type = self.check_expr(node.expr)
        node.expr = expr_node

        # Same type: valid
        if var_type == expr_type:
            return node

        # Numeric assignment
        if is_numeric(var_type) and is_numeric(expr_type):
            node.expr = Cast(
                var_type,
                node.expr,
                lineno=node.lineno
            )
            return node

        # Everything else is invalid
        self.error(
            "invalid assignment",
            node.lineno
        )

        return node

    def check_print(self, node):
        expr_node, expr_type = self.check_expr(node.expr)
        node.expr = expr_node
        return node

    def check_stmt(self, node):
        if isinstance(node, Assign):
            return self.check_assign_stmt(node)

        if isinstance(node, Print):
            return self.check_print(node)

        return node

    def check_function(self, function):
        self.symbol_table = function.getLocalSymbolTable()

        checked_statements = []

        for stmt in function.getStatementsAstList():
            checked_statements.append(
                self.check_stmt(stmt)
            )

        function.setStatementsAstList(checked_statements)

        return function

def check_program(program):
    errors = []

    for function in program.getFunctions():
        checker = TypeChecker(function.getLocalSymbolTable())
        checker.check_function(function)
        errors.extend(checker.errors)

    return errors

