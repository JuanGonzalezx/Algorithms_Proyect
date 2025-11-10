# app/modules/parser/agent.py
from pathlib import Path
from typing import List
from lark import Lark, Transformer, Tree, Token, v_args
from app.models.ast_nodes import (
    Program, Function, Param, Block,
    Assign, If, While, For, Return, ExprStmt,
    Var, Literal, BinOp, UnOp, Compare, Call, ArrayAccess,
    Expr, Stmt
)


# ---------- Transformer: Lark parse tree -> AST ----------
class PseudocodeToASTTransformer(Transformer):
    def _block(self, children: List[Stmt]) -> Block:
        return Block(statements=[c for c in children if isinstance(c, Stmt)])

    def _meta_lines(self, meta):
        return getattr(meta, "line", None), getattr(meta, "end_line", None)

    # ===== Programa / funciones =====
    def start(self, children):
        functions = [c for c in children if isinstance(c, Function)]
        return Program(functions=functions)

    def statement(self, children):
        return children[0]

    def procedure_def(self, children):
        name = str(children[0])
        params: List[Param] = []
        stmts: List[Stmt] = []
        for ch in children[1:]:
            if isinstance(ch, list):
                params = ch
            elif isinstance(ch, Stmt):
                stmts.append(ch)
        return Function(name=name, params=params, body=Block(statements=stmts))

    def parameter_list(self, children):
        return children

    def parameter(self, children):
        for ch in children:
            if isinstance(ch, Token) and ch.type == "NAME":
                return Param(name=str(ch))
        return Param(name="")

    # ===== Sentencias =====
    @v_args(meta=True)
    def assignment(self, meta, children):
        line_start, line_end = self._meta_lines(meta)
        return Assign(target=children[0], value=children[1],
                      line_start=line_start, line_end=line_end)

    def lvalue(self, children):
        if len(children) == 1:
            return Var(name=str(children[0]))
        name = str(children[0])
        if isinstance(children[1], Expr):
            return ArrayAccess(array=Var(name=name), index=children[1])
        return Var(name=f"{name}.{children[1]}")

    @v_args(meta=True)
    def if_statement(self, meta, children):
        cond, then_block = children[0], children[1]
        else_block = children[2] if len(children) > 2 else None
        line_start, line_end = self._meta_lines(meta)
        return If(cond=cond, then_block=then_block, else_block=else_block,
                  line_start=line_start, line_end=line_end)

    def then_part(self, children):
        return self._block(children)

    def else_part(self, children):
        return self._block(children)

    @v_args(meta=True)
    def while_loop(self, meta, children):
        cond = children[0]
        body = self._block(children[1:])
        line_start, line_end = self._meta_lines(meta)
        return While(cond=cond, body=body, line_start=line_start, line_end=line_end)

    @v_args(meta=True)
    def for_loop(self, meta, children):
        var_name = str(children[0])
        start, end = children[1], children[2]
        body = self._block(children[3:])
        line_start, line_end = self._meta_lines(meta)
        return For(var=var_name, start=start, end=end, body=body,
                   line_start=line_start, line_end=line_end)

    def repeat_loop(self, children):
        body, cond = children[0], children[1]
        return While(cond=UnOp(op="not", operand=cond), body=body)

    @v_args(meta=True)
    def return_statement(self, meta, children):
        line_start, line_end = self._meta_lines(meta)
        return Return(value=children[0] if children else None,
                      line_start=line_start, line_end=line_end)

    def expr_stmt(self, children):
        return ExprStmt(expr=children[0])

    # ===== Expresiones =====
    def expr(self, children):
        return children[0]

    def or_expr(self, children):
        if len(children) == 1: return children[0]
        res = children[0]
        for ch in children[1:]:
            if isinstance(ch, Token): continue
            res = BinOp(op="or", left=res, right=ch)
        return res

    def and_expr(self, children):
        if len(children) == 1: return children[0]
        res = children[0]
        for ch in children[1:]:
            if isinstance(ch, Token): continue
            res = BinOp(op="and", left=res, right=ch)
        return res

    def not_expr(self, children):
        return UnOp(op="not", operand=children[1]) if len(children) == 2 else children[0]

    def comparison(self, children):
        if len(children) == 1:
            return children[0]
        left, op_token, right = children[0], children[1], children[2]
        op = str(op_token)
        op = {
            "=": "==", "==": "==",
            "≠": "!=", "!=": "!=", "<>": "!=",
            "≤": "<=", "<=": "<=",
            "≥": ">=", ">=": ">=",
        }.get(op, op)
        return Compare(op=op, left=left, right=right)

    def arith_expr(self, children):
        if len(children) == 1: return children[0]
        res, i = children[0], 1
        while i < len(children):
            res = BinOp(op=str(children[i]), left=res, right=children[i+1])
            i += 2
        return res

    def term(self, children):
        if len(children) == 1: return children[0]
        res, i = children[0], 1
        while i < len(children):
            res = BinOp(op=str(children[i]), left=res, right=children[i+1])
            i += 2
        return res

    def condition(self, children):
        return children[0]

    # ----- Átomos -----
    def number(self, children):
        val = str(children[0])
        return Literal(value=int(val) if "." not in val else float(val))

    def variable(self, children):
        return Var(name=str(children[0]))

    def function_call(self, children):
        name = str(children[0])
        args = children[1] if len(children) > 1 and isinstance(children[1], list) else []
        return Call(name=name, args=args)

    def argument_list(self, children):
        return children

    def array_access(self, children):
        base = ArrayAccess(array=Var(name=str(children[0])), index=children[1])
        for extra in children[2:]:
            if isinstance(extra, Expr):
                base = ArrayAccess(array=base, index=extra)
        return base

    def field_access(self, children):
        return Var(name=f"{children[0]}.{children[1]}")


# ---------- Agente ----------
class ParserAgent:
    """Convierte pseudocódigo a AST tipado usando la gramática compartida."""

    def __init__(self):
        self.grammar_path = (
            Path(__file__).parent.parent.parent / "shared" / "grammar" / "grammar.lark"
        )
        self.transformer = PseudocodeToASTTransformer()
        self._load_grammar()

    def _load_grammar(self):
        if not self.grammar_path.exists():
            raise FileNotFoundError(f"Gramática no encontrada: {self.grammar_path}")
        with open(self.grammar_path, "r", encoding="utf-8") as f:
            grammar = f.read()
        # Mantiene start="start" como en tu gramática original
        self.parser = Lark(
            grammar,
            start="start",
            parser="lalr",
            propagate_positions=True,
            maybe_placeholders=False,
        )

    def parse(self, pseudocode: str) -> Program:
        tree = self.parser.parse(pseudocode)
        return self.transformer.transform(tree)

    def __call__(self, input_data: dict) -> dict:
        try:
            ast = self.parse(input_data.get("pseudocode", ""))
            return {"ast": ast, "success": True, "error": None}
        except Exception as e:
            return {"ast": None, "success": False, "error": str(e)}


# ---------- Singleton ----------
_parser_agent: ParserAgent | None = None

def get_parser_agent() -> ParserAgent:
    global _parser_agent
    if _parser_agent is None:
        _parser_agent = ParserAgent()
    return _parser_agent
