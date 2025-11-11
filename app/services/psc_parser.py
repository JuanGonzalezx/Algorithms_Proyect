"""
Parser de pseudocódigo → IR usando Lark.
Convierte árbol Lark → nuestro IR (ast_nodes).
"""
from pathlib import Path
from typing import List

from lark import Lark, Transformer, Token

from app.services.ast_nodes import (
    Program, Function, Param, Block, Stmt, Expr,
    Assign, Return, ExprStmt, If, While, For,
    Literal, Var, ArrayAccess, BinOp, UnOp, Compare, Call
)

# Gramática esperada en: app/modules/parser/grammar/pseudocode.lark
GRAMMAR_PATH = Path(__file__).parent / "grammar" / "pseudocode.lark"


class PseudocodeToIR(Transformer):
    """Transformer Lark → IR."""

    # ===================== Programa y funciones =====================

    def start(self, items):
        """Punto de entrada: lista de statements (procedimientos)."""
        functions: List[Function] = [it for it in items if isinstance(it, Function)]
        return Program(functions=functions)

    def procedure_def(self, items):
        """Definición de procedimiento: nombre, params?, cuerpo."""
        name = str(items[0])
        params: List[Param] = []
        body_stmts: List[Stmt] = []
        for it in items[1:]:
            if isinstance(it, list):         # parameter_list
                params = it
            elif isinstance(it, Stmt):       # statements del cuerpo
                body_stmts.append(it)
        return Function(name=name, params=params, body=Block(statements=body_stmts))

    def parameter_list(self, items):
        return items

    def parameter(self, items):
        return Param(name=str(items[0]))

    # =========================== Sentencias ==========================

    def var_declaration(self, _):
        """Declaración de variables: se ignora (no afecta el IR)."""
        return None

    def statement(self, items):
        """Envuelve un statement; filtra None (declaraciones)."""
        if not items:
            return None
        return items[0] if items[0] is not None else None

    def lvalue(self, items):
        """Lado izquierdo: var | name[index] | name.field."""
        if len(items) == 1:
            return Var(name=str(items[0]))
        if len(items) == 2:  # name[index]
            return ArrayAccess(array=Var(name=str(items[0])), index=items[1])
        if len(items) == 3:  # name . field  (simplificado a Var compuesta)
            return Var(name=f"{items[0]}.{items[2]}")
        return items[0]

    def assignment(self, items):
        return Assign(target=items[0], value=items[1])

    def return_statement(self, items):
        return Return(value=items[0] if items else None)

    def call_statement(self, items):
        return ExprStmt(expr=items[0])

    def then_part(self, items):
        stmts = [it for it in items if isinstance(it, Stmt)]
        return Block(statements=stmts)

    def else_part(self, items):
        stmts = [it for it in items if isinstance(it, Stmt)]
        return Block(statements=stmts)

    def if_statement(self, items):
        cond = items[0]
        then_block = items[1]
        else_block = items[2] if len(items) > 2 else None
        return If(cond=cond, then_block=then_block, else_block=else_block)

    def while_loop(self, items):
        cond = items[0]
        body_stmts = [it for it in items[1:] if isinstance(it, Stmt)]
        return While(cond=cond, body=Block(statements=body_stmts))

    def for_loop(self, items):
        var_name = str(items[0])
        start_expr, end_expr = items[1], items[2]
        body_stmts = [it for it in items[3:] if isinstance(it, Stmt)]
        return For(var=var_name, start=start_expr, end=end_expr, body=Block(statements=body_stmts))

    def repeat_loop(self, items):
        """repeat ... until (cond)  ⇒ while not(cond) do ..."""
        cond = items[-1]
        body_stmts = [it for it in items[:-1] if isinstance(it, Stmt)]
        return While(cond=UnOp(op="not", operand=cond), body=Block(statements=body_stmts))

    # =========================== Expresiones ==========================

    def number(self, items):
        s = str(items[0])
        return Literal(value=float(s) if "." in s else int(s))

    def variable(self, items):
        return Var(name=str(items[0]))

    def array_access(self, items):
        """arr[i][j] => ArrayAccess(ArrayAccess(Var(arr), i), j)"""
        result: Expr = Var(name=str(items[0]))
        for idx in items[1:]:
            result = ArrayAccess(array=result, index=idx)
        return result

    def function_call(self, items):
        func_name = str(items[0])
        args = [it for it in items[1:] if isinstance(it, Expr)]
        return Call(name=func_name, args=args)

    def true_value(self, _):
        return Literal(value=True)

    def false_value(self, _):
        return Literal(value=False)

    def null_value(self, _):
        return Literal(value=None)

    def field_access(self, items):
        return Var(name=f"{items[0]}.{items[1]}")

    # ============================ Operadores ==========================

    def or_expr(self, items):
        if len(items) == 1:
            return items[0]
        out = items[0]
        for it in items[1:]:
            out = BinOp(op="or", left=out, right=it)
        return out

    def and_expr(self, items):
        if len(items) == 1:
            return items[0]
        out = items[0]
        for it in items[1:]:
            out = BinOp(op="and", left=out, right=it)
        return out

    def not_expr(self, items):
        return items[0] if len(items) == 1 else UnOp(op="not", operand=items[0])

    def comparison(self, items):
        if len(items) == 1:
            return items[0]
        op_map = {
            "<": "<", ">": ">", "≤": "<=", "≥": ">=", "<=": "<=", ">=": ">=",
            "=": "=", "≠": "!=", "==": "=", "!=": "!=",
        }
        left, op_tok, right = items[0], items[1], items[2]
        op = str(op_tok) if isinstance(op_tok, Token) else str(op_tok)
        return Compare(op=op_map.get(op, op), left=left, right=right)

    def arith_expr(self, items):
        if len(items) == 1:
            return items[0]
        out = items[0]
        i = 1
        while i < len(items):
            if isinstance(items[i], Token):
                op = "+" if items[i].type == "PLUS" else "-"
                out = BinOp(op=op, left=out, right=items[i + 1])
                i += 2
            else:
                out = BinOp(op="+", left=out, right=items[i])
                i += 1
        return out

    def term(self, items):
        if len(items) == 1:
            return items[0]
        out = items[0]
        i = 1
        while i < len(items):
            if isinstance(items[i], Token):
                t = items[i].type
                op = "*" if t == "STAR" else "/" if t == "SLASH" else "div" if t == "DIV" else "mod"
                out = BinOp(op=op, left=out, right=items[i + 1])
                i += 2
            else:
                out = BinOp(op="*", left=out, right=items[i])
                i += 1
        return out

    def ceiling(self, items):
        return Call(name="ceiling", args=[items[0]])

    def floor(self, items):
        return Call(name="floor", args=[items[0]])

    def argument_list(self, items):
        return items

    def condition(self, items):
        return items[0]

    # ============================ Helpers =============================

    def action_statement(self, _):
        """Acción vacía."""
        return ExprStmt(expr=Literal(value=None))


class PseudocodeParser:
    """Parser de pseudocódigo → IR."""

    def __init__(self):
        grammar = GRAMMAR_PATH.read_text(encoding="utf-8")
        self.parser = Lark(grammar, start="start", parser="lalr")
        self.transformer = PseudocodeToIR()

    def build(self, code: str) -> Program:
        """Parsea pseudocódigo y construye Program IR."""
        try:
            tree = self.parser.parse(code)
            return self.transformer.transform(tree)
        except Exception as e:
            raise Exception(f"Error parsing pseudocode: {e}")


__all__ = ["PseudocodeParser", "PseudocodeToIR"]
