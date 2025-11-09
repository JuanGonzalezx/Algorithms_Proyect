"""
Representación intermedia (IR) del AST usando dataclasses.
Independiente del lenguaje fuente, diseñado para análisis de complejidad.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Union, Any, Dict


# ============================================================================
# EXPRESIONES
# ============================================================================

@dataclass
class Expr:
    """Expresión base"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa el nodo a diccionario"""
        return asdict(self)


@dataclass
class Literal(Expr):
    """Literal: número, string, bool, None"""
    value: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Literal",
            "value": self.value
        }


@dataclass
class Var(Expr):
    """Variable o identificador"""
    name: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Var",
            "name": self.name
        }


@dataclass
class ArrayAccess(Expr):
    """Acceso a arreglo: arr[index]"""
    array: Var = field(default_factory=lambda: Var())
    index: Expr = field(default_factory=lambda: Literal())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ArrayAccess",
            "array": self.array.to_dict(),
            "index": self.index.to_dict()
        }


@dataclass
class BinOp(Expr):
    """Operación binaria: +, -, *, /, div, mod, and, or"""
    op: str = "+"
    left: Expr = field(default_factory=lambda: Literal())
    right: Expr = field(default_factory=lambda: Literal())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "BinOp",
            "op": self.op,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }


@dataclass
class UnOp(Expr):
    """Operación unaria: -, not"""
    op: str = "-"
    operand: Expr = field(default_factory=lambda: Literal())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "UnOp",
            "op": self.op,
            "operand": self.operand.to_dict()
        }


@dataclass
class Compare(Expr):
    """Comparación: =, !=, <, <=, >, >="""
    op: str = "="
    left: Expr = field(default_factory=lambda: Literal())
    right: Expr = field(default_factory=lambda: Literal())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Compare",
            "op": self.op,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }


@dataclass
class Call(Expr):
    """Llamada a función: f(args)"""
    name: str = ""
    args: List[Expr] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Call",
            "name": self.name,
            "args": [arg.to_dict() for arg in self.args]
        }


# ============================================================================
# SENTENCIAS
# ============================================================================

@dataclass
class Stmt:
    """Sentencia base"""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Assign(Stmt):
    """Asignación: target = value"""
    target: Union[Var, ArrayAccess] = field(default_factory=lambda: Var())
    value: Expr = field(default_factory=lambda: Literal())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Assign",
            "target": self.target.to_dict(),
            "value": self.value.to_dict()
        }


@dataclass
class Return(Stmt):
    """Return statement"""
    value: Optional[Expr] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Return",
            "value": self.value.to_dict() if self.value else None
        }


@dataclass
class ExprStmt(Stmt):
    """Statement que es una expresión (ej: llamada a función)"""
    expr: Expr = field(default_factory=lambda: Literal())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ExprStmt",
            "expr": self.expr.to_dict()
        }


@dataclass
class Block:
    """Bloque de sentencias"""
    statements: List[Stmt] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Block",
            "statements": [stmt.to_dict() for stmt in self.statements]
        }


@dataclass
class If(Stmt):
    """Condicional if/else"""
    cond: Expr = field(default_factory=lambda: Literal())
    then_block: Block = field(default_factory=Block)
    else_block: Optional[Block] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "If",
            "cond": self.cond.to_dict(),
            "then_block": self.then_block.to_dict(),
            "else_block": self.else_block.to_dict() if self.else_block else None
        }


@dataclass
class While(Stmt):
    """Bucle while"""
    cond: Expr = field(default_factory=lambda: Literal())
    body: Block = field(default_factory=Block)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "While",
            "cond": self.cond.to_dict(),
            "body": self.body.to_dict()
        }


@dataclass
class For(Stmt):
    """Bucle for con rango: for var in range(start, end)
    Nota: Python usa [start, end), nuestro IR también.
    """
    var: str = ""
    start: Expr = field(default_factory=lambda: Literal(0))
    end: Expr = field(default_factory=lambda: Literal(0))
    body: Block = field(default_factory=Block)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "For",
            "var": self.var,
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "body": self.body.to_dict()
        }


# ============================================================================
# ESTRUCTURAS DE ALTO NIVEL
# ============================================================================

@dataclass
class Param:
    """Parámetro de función"""
    name: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name}


@dataclass
class Function:
    """Definición de función"""
    name: str = ""
    params: List[Param] = field(default_factory=list)
    body: Block = field(default_factory=Block)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Function",
            "name": self.name,
            "params": [p.to_dict() for p in self.params],
            "body": self.body.to_dict()
        }


@dataclass
class Program:
    """Programa completo (colección de funciones)"""
    functions: List[Function] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Program",
            "functions": [f.to_dict() for f in self.functions]
        }