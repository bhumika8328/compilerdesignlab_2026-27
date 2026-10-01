<<<<<<< HEAD
from SymbolTable import DataType
from ast_nodes import (
    Const, Var, Assign, Print, BinOp,
    RelOp, Cast, Ternary
)
from type_rules import SemanticError, is_numeric, promote


# ============================================================
# Variable
# ============================================================

def check_var(node, symbol_table, errors):
    symbol = symbol_table.getSymbol(node.name)

    if symbol is None:
        errors.append(
            SemanticError(
                f"undeclared variable '{node.name}'",
                node.lineno
            )
        )
        return None

    return symbol.getDataType()


# ============================================================
# Assignment
# ============================================================

def check_assign_stmt(node, symbol_table, errors):
    symbol = symbol_table.getSymbol(node.var.name)

    if symbol is None:
        errors.append(
            SemanticError(
                f"undeclared variable '{node.var.name}'",
                node.lineno
            )
        )
        return None

    expr_type = check_expr(node.expr, symbol_table, errors)

    if expr_type is None:
        return None

    target_type = symbol.getDataType()

    # Same type
    if target_type == expr_type:
        return target_type

    # INT -> DOUBLE is allowed.
    # The actual Cast node is inserted into the AST.
    if target_type == DataType.DOUBLE and expr_type == DataType.INT:
        node.expr = Cast(
            DataType.DOUBLE,
            node.expr,
            node.expr.lineno
        )
        return target_type

    # All other mismatches are errors.
    errors.append(
        SemanticError(
            f"cannot assign {expr_type} to {target_type}",
            node.lineno
        )
    )

    return None


# ============================================================
# Binary operation
# ============================================================

def check_binop(node, symbol_table, errors):
    left_type = check_expr(node.left, symbol_table, errors)
    right_type = check_expr(node.right, symbol_table, errors)

    if left_type is None or right_type is None:
        return None

    # Binary arithmetic operations require numeric operands.
    if not is_numeric(left_type) or not is_numeric(right_type):
        errors.append(
            SemanticError(
                f"invalid operands for '{node.op}'",
                node.lineno
            )
        )
        return None

    result_type = promote(left_type, right_type)

    # INT + DOUBLE -> cast INT to DOUBLE
    if result_type == DataType.DOUBLE:

        if left_type == DataType.INT:
            node.left = Cast(
                DataType.DOUBLE,
                node.left,
                node.left.lineno
            )

        if right_type == DataType.INT:
            node.right = Cast(
                DataType.DOUBLE,
                node.right,
                node.right.lineno
            )

    return result_type


# ============================================================
# Relational operation
# ============================================================

def check_relop(node, symbol_table, errors):
    left_type = check_expr(node.left, symbol_table, errors)
    right_type = check_expr(node.right, symbol_table, errors)

    if left_type is None or right_type is None:
        return None

    # --------------------------------------------------------
    # Numeric comparison
    # INT < DOUBLE
    # DOUBLE > INT
    # etc.
    # --------------------------------------------------------

    if is_numeric(left_type) and is_numeric(right_type):

        result_type = promote(left_type, right_type)

        # INT -> DOUBLE promotion
        if result_type == DataType.DOUBLE:

            if left_type == DataType.INT:
                node.left = Cast(
                    DataType.DOUBLE,
                    node.left,
                    node.left.lineno
                )

            if right_type == DataType.INT:
                node.right = Cast(
                    DataType.DOUBLE,
                    node.right,
                    node.right.lineno
                )

        # Relational expression produces INT
        return DataType.INT

    # --------------------------------------------------------
    # Same non-numeric types
    # --------------------------------------------------------

    if left_type == right_type:
        return DataType.INT

    # --------------------------------------------------------
    # Different incompatible types
    # --------------------------------------------------------

    errors.append(
        SemanticError(
            f"invalid operands for relational operator "
            f"'{node.op}': {left_type} and {right_type}",
            node.lineno
        )
    )

    return None


# ============================================================
# Cast
# ============================================================

def check_cast(node, symbol_table, errors):
    expr_type = check_expr(node.expr, symbol_table, errors)

    if expr_type is None:
        return None

    target_type = node.target_type

    # Same type
    if expr_type == target_type:
        return target_type

    # Numeric conversions
    if is_numeric(expr_type) and is_numeric(target_type):
        return target_type

    # CHAR -> INT
    if expr_type == DataType.CHAR and target_type == DataType.INT:
        return target_type

    # INT -> CHAR
    if expr_type == DataType.INT and target_type == DataType.CHAR:
        return target_type

    errors.append(
        SemanticError(
            f"invalid cast from {expr_type} to {target_type}",
            node.lineno
        )
    )

    return None


# ============================================================
# Ternary
# condition ? then_expr : else_expr
# ============================================================

def check_ternary(node, symbol_table, errors):

    cond_type = check_expr(
        node.cond,
        symbol_table,
        errors
    )

    then_type = check_expr(
        node.then_expr,
        symbol_table,
        errors
    )

    else_type = check_expr(
        node.else_expr,
        symbol_table,
        errors
    )

    if cond_type is None or then_type is None or else_type is None:
        return None

    # --------------------------------------------------------
    # Condition must be numeric
    # --------------------------------------------------------

    if not is_numeric(cond_type):
        errors.append(
            SemanticError(
                "ternary condition must be numeric",
                node.cond.lineno
            )
        )

    # --------------------------------------------------------
    # Same result types
    # --------------------------------------------------------

    if then_type == else_type:
        return then_type

    # --------------------------------------------------------
    # INT ? DOUBLE : INT
    # DOUBLE ? INT : DOUBLE
    #
    # Promote INT to DOUBLE.
    # --------------------------------------------------------

    if is_numeric(then_type) and is_numeric(else_type):

        result_type = promote(then_type, else_type)

        if result_type == DataType.DOUBLE:

            if then_type == DataType.INT:
                node.then_expr = Cast(
                    DataType.DOUBLE,
                    node.then_expr,
                    node.then_expr.lineno
                )

            if else_type == DataType.INT:
                node.else_expr = Cast(
                    DataType.DOUBLE,
                    node.else_expr,
                    node.else_expr.lineno
                )

        return result_type

    # --------------------------------------------------------
    # Incompatible types
    # --------------------------------------------------------

    errors.append(
        SemanticError(
            f"incompatible types in ternary expression: "
            f"{then_type} and {else_type}",
            node.lineno
        )
    )

    return None


# ============================================================
# Expression
# ============================================================

def check_expr(node, symbol_table, errors):

    if isinstance(node, Const):
        return node.type

    if isinstance(node, Var):
        return check_var(
            node,
            symbol_table,
            errors
        )

    if isinstance(node, BinOp):
        return check_binop(
            node,
            symbol_table,
            errors
        )

    if isinstance(node, RelOp):
        return check_relop(
            node,
            symbol_table,
            errors
        )

    if isinstance(node, Cast):
        return check_cast(
            node,
            symbol_table,
            errors
        )

    if isinstance(node, Ternary):
        return check_ternary(
            node,
            symbol_table,
            errors
        )

    return None


# ============================================================
# Statement
# ============================================================

def check_stmt(node, symbol_table, errors):

    if isinstance(node, Assign):
        return check_assign_stmt(
            node,
            symbol_table,
            errors
        )

    if isinstance(node, Print):
        return check_expr(
            node.expr,
            symbol_table,
            errors
        )

    return None


# ============================================================
# Program
# ============================================================

def check_program(program):

    errors = []

    for func in program.getFunctions():

        symbol_table = func.getLocalSymbolTable()

        for stmt in func.getStatementsAstList():

            check_stmt(
                stmt,
                symbol_table,
                errors
            )
=======
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

        return node, DataType.INT

    def check_cast(self, node):
        expr_node, expr_type = self.check_expr(node.expr)
        node.expr = expr_node

        target_type = node.target_type

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

        if not is_numeric(cond_type):
            self.error(
                "invalid ternary condition",
                node.lineno
            )

        if then_type == else_type:
            return node, then_type

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

        self.error(
            "incompatible ternary expressions",
            node.lineno
        )

        return node, then_type

    def check_assign_stmt(self, node):
        var_node, var_type = self.check_var(node.var)
        node.var = var_node
        expr_node, expr_type = self.check_expr(node.expr)
        node.expr = expr_node
        if var_type == expr_type:
            return node

        if is_numeric(var_type) and is_numeric(expr_type):
            node.expr = Cast(
                var_type,
                node.expr,
                lineno=node.lineno
            )
            return node

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
>>>>>>> usha/main

    return errors
