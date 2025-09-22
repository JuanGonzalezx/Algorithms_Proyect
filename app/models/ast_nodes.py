from dataclasses import dataclass
from typing import List, Optional, Any

@dataclass
class ASTNode:
    """Nodo base del AST"""
    node_type: str
    value: Optional[str] = None
    children: List['ASTNode'] = None
    line: Optional[int] = None
    column: Optional[int] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []

@dataclass
class Program(ASTNode):
    """Nodo raíz del programa"""
    def __post_init__(self):
        super().__post_init__()
        self.node_type = "program"

@dataclass
class Procedure(ASTNode):
    """Nodo de procedimiento/función"""
    name: str = ""
    parameters: List[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.node_type = "procedure"
        if self.parameters is None:
            self.parameters = []

@dataclass
class ForLoop(ASTNode):
    """Nodo de bucle for"""
    variable: str = ""
    start_expr: Optional['ASTNode'] = None
    end_expr: Optional['ASTNode'] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.node_type = "for_loop"

@dataclass
class WhileLoop(ASTNode):
    """Nodo de bucle while"""
    condition: Optional['ASTNode'] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.node_type = "while_loop"

@dataclass
class IfStatement(ASTNode):
    """Nodo de condicional if"""
    condition: Optional['ASTNode'] = None
    then_body: List['ASTNode'] = None
    else_body: List['ASTNode'] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.node_type = "if_statement"
        if self.then_body is None:
            self.then_body = []
        if self.else_body is None:
            self.else_body = []

@dataclass
class Assignment(ASTNode):
    """Nodo de asignación"""
    target: str = ""
    expression: Optional['ASTNode'] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.node_type = "assignment"

@dataclass
class FunctionCall(ASTNode):
    """Nodo de llamada a función"""
    function_name: str = ""
    arguments: List['ASTNode'] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.node_type = "function_call"
        if self.arguments is None:
            self.arguments = []

@dataclass
class Expression(ASTNode):
    """Nodo de expresión"""
    operator: Optional[str] = None
    left: Optional['ASTNode'] = None
    right: Optional['ASTNode'] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.node_type = "expression"

@dataclass
class Variable(ASTNode):
    """Nodo de variable"""
    name: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.node_type = "variable"

@dataclass
class Number(ASTNode):
    """Nodo de número"""
    value: int = 0
    
    def __post_init__(self):
        super().__post_init__()
        self.node_type = "number"