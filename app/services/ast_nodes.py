"""
IR (AST) minimalista para análisis de complejidad.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

# ==============================
# Expresiones
# ==============================

@dataclass
class Expr:
    """Clase base de expresiones."""
    def to_dict(self) -> Dict[str, Any]:
        # Cada subclase implementa su propio to_dict.
        return {"type": self.__class__.__name__}

@dataclass
class Literal(Expr):
    value: Any = None
    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Literal", "value": self.value}

@dataclass
class Var(Expr):
    name: str = ""
    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Var", "name": self.name}

@dataclass
class ArrayAccess(Expr):
    array: Var = field(default_factory=Var)
    index: Expr = field(default_factory=Literal)
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ArrayAccess",
            "array": self.array.to_dict(),
            "index": self.index.to_dict(),
        }

@dataclass
class BinOp(Expr):
    op: str = "+"
    left: Expr = field(default_factory=Literal)
    right: Expr = field(default_factory=Literal)
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "BinOp",
            "op": self.op,
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
        }

@dataclass
class UnOp(Expr):
    op: str = "-"
    operand: Expr = field(default_factory=Literal)
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "UnOp",
            "op": self.op,
            "operand": self.operand.to_dict(),
        }

@dataclass
class Compare(Expr):
    op: str = "="
    left: Expr = field(default_factory=Literal)
    right: Expr = field(default_factory=Literal)
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Compare",
            "op": self.op,
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
        }

@dataclass
class Call(Expr):
    name: str = ""
    args: List[Expr] = field(default_factory=list)
    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Call", "name": self.name, "args": [a.to_dict() for a in self.args]}

# ==============================
# Sentencias
# ==============================

@dataclass
class Stmt:
    """Clase base de sentencias con metadatos de línea."""
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    def to_dict(self) -> Dict[str, Any]:
        out = {"type": self.__class__.__name__}
        if self.line_start is not None:
            out["line_start"] = self.line_start
        if self.line_end is not None:
            out["line_end"] = self.line_end
        return out

@dataclass
class Assign(Stmt):
    target: Union[Var, ArrayAccess] = field(default_factory=Var)
    value: Expr = field(default_factory=Literal)
    def to_dict(self) -> Dict[str, Any]:
        out = super().to_dict()
        out.update({
            "target": self.target.to_dict(),
            "value": self.value.to_dict(),
        })
        return out

@dataclass
class Return(Stmt):
    value: Optional[Expr] = None
    def to_dict(self) -> Dict[str, Any]:
        out = super().to_dict()
        out["value"] = self.value.to_dict() if self.value else None
        return out

@dataclass
class ExprStmt(Stmt):
    expr: Expr = field(default_factory=Literal)
    def to_dict(self) -> Dict[str, Any]:
        out = super().to_dict()
        out["expr"] = self.expr.to_dict()
        return out

@dataclass
class Block:
    statements: List[Stmt] = field(default_factory=list)
    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Block", "statements": [s.to_dict() for s in self.statements]}

@dataclass
class If(Stmt):
    cond: Expr = field(default_factory=Literal)
    then_block: Block = field(default_factory=Block)
    else_block: Optional[Block] = None
    def to_dict(self) -> Dict[str, Any]:
        out = super().to_dict()
        out.update({
            "cond": self.cond.to_dict(),
            "then_block": self.then_block.to_dict(),
            "else_block": self.else_block.to_dict() if self.else_block else None,
        })
        return out

@dataclass
class While(Stmt):
    cond: Expr = field(default_factory=Literal)
    body: Block = field(default_factory=Block)
    def to_dict(self) -> Dict[str, Any]:
        out = super().to_dict()
        out.update({
            "cond": self.cond.to_dict(),
            "body": self.body.to_dict(),
        })
        return out

@dataclass
class For(Stmt):
    """
    Bucle for con rango inclusivo: [start, end], acorde a SymPy Sum(var, start, end).
    """
    var: str = ""
    start: Expr = field(default_factory=Literal)
    end: Expr = field(default_factory=Literal)
    body: Block = field(default_factory=Block)
    def to_dict(self) -> Dict[str, Any]:
        out = super().to_dict()
        out.update({
            "var": self.var,
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "body": self.body.to_dict(),
        })
        return out

# ==============================
# Alto nivel
# ==============================

@dataclass
class Param:
    name: str = ""
    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name}

@dataclass
class Function:
    name: str = ""
    params: List[Param] = field(default_factory=list)
    body: Block = field(default_factory=Block)
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Function",
            "name": self.name,
            "params": [p.to_dict() for p in self.params],
            "body": self.body.to_dict(),
        }

@dataclass
class Program:
    functions: List[Function] = field(default_factory=list)
    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Program", "functions": [f.to_dict() for f in self.functions]}

__all__ = [
    "Expr", "Literal", "Var", "ArrayAccess", "BinOp", "UnOp", "Compare", "Call",
    "Stmt", "Assign", "Return", "ExprStmt", "Block", "If", "While", "For",
    "Param", "Function", "Program",
]
