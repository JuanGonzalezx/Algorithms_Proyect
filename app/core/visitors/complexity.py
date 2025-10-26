"""
Visitor para análisis de complejidad computacional.
Esqueleto básico para Fase 2.
"""
from typing import Union, Any
from app.models.ast_nodes import (
    Program, Function, Block, Stmt, Expr,
    Assign, Return, ExprStmt, If, While, For,
    Literal, Var, ArrayAccess, BinOp, UnOp, Compare, Call
)


class Complexity:
    """
    Visitor que calcula complejidad computacional simbólica.
    
    Por ahora retorna strings simbólicos como placeholders.
    En Fase 2 se integrará con Sympy para análisis real.
    """
    
    @staticmethod
    def of(node: Union[Stmt, Expr, Block, Function, Program]) -> str:
        """
        Calcula la complejidad de un nodo.
        
        Returns:
            String representando la complejidad (ej: "O(n)", "O(1)")
        """
        visitor = Complexity()
        return visitor.visit(node)
    
    def visit(self, node: Any) -> str:
        """Despacha al método visit_* apropiado"""
        method_name = f"visit_{node.__class__.__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def generic_visit(self, node: Any) -> str:
        """Fallback para nodos sin visitor específico"""
        return "O(?)"
    
    # ========================================================================
    # EXPRESIONES (generalmente O(1))
    # ========================================================================
    
    def visit_Literal(self, node: Literal) -> str:
        return "O(1)"
    
    def visit_Var(self, node: Var) -> str:
        return "O(1)"
    
    def visit_ArrayAccess(self, node: ArrayAccess) -> str:
        # Acceso: O(1), pero el índice puede tener costo
        index_cost = self.visit(node.index)
        if index_cost == "O(1)":
            return "O(1)"
        return f"O(1) + {index_cost}"
    
    def visit_BinOp(self, node: BinOp) -> str:
        left = self.visit(node.left)
        right = self.visit(node.right)
        # Simplificación básica
        if left == "O(1)" and right == "O(1)":
            return "O(1)"
        return f"max({left}, {right})"
    
    def visit_UnOp(self, node: UnOp) -> str:
        operand = self.visit(node.operand)
        return operand
    
    def visit_Compare(self, node: Compare) -> str:
        left = self.visit(node.left)
        right = self.visit(node.right)
        if left == "O(1)" and right == "O(1)":
            return "O(1)"
        return f"max({left}, {right})"
    
    def visit_Call(self, node: Call) -> str:
        # Por ahora asumimos llamadas O(1)
        # En Fase 2 se buscará la definición de la función
        return "O(1)"
    
    # ========================================================================
    # SENTENCIAS
    # ========================================================================
    
    def visit_Assign(self, node: Assign) -> str:
        """Asignación: costo de evaluar la expresión"""
        value_cost = self.visit(node.value)
        return value_cost if value_cost != "O(1)" else "O(1)"
    
    def visit_Return(self, node: Return) -> str:
        """Return: costo de evaluar el valor"""
        if node.value:
            return self.visit(node.value)
        return "O(1)"
    
    def visit_ExprStmt(self, node: ExprStmt) -> str:
        """Statement de expresión: costo de la expresión"""
        return self.visit(node.expr)
    
    def visit_If(self, node: If) -> str:
        """
        If: peor caso = costo(condición) + max(then_block, else_block)
        """
        cond_cost = self.visit(node.cond)
        then_cost = self.visit(node.then_block)
        else_cost = self.visit(node.else_block) if node.else_block else "O(1)"
        
        # Placeholder simbólico
        return f"{cond_cost} + max({then_cost}, {else_cost})"
    
    def visit_While(self, node: While) -> str:
        """
        While: O(k) * (body_cost)
        donde k es número de iteraciones (desconocido)
        """
        body_cost = self.visit(node.body)
        return f"O(k) * ({body_cost})"
    
    def visit_For(self, node: For) -> str:
        """
        For: O(end - start) * (body_cost)
        
        Placeholder: retorna "O(n) * (body_cost)"
        En Fase 2 se calculará el rango exacto.
        """
        body_cost = self.visit(node.body)
        # Placeholder simbólico
        return f"O(n) * ({body_cost})"
    
    def visit_Block(self, node: Block) -> str:
        """
        Block: suma de complejidades de cada statement.
        Simplificación: retorna la máxima.
        """
        if not node.statements:
            return "O(1)"
        
        costs = [self.visit(stmt) for stmt in node.statements]
        
        # Simplificación: retornar la última (o max en Fase 2)
        return costs[-1] if costs else "O(1)"
    
    def visit_Function(self, node: Function) -> str:
        """Function: complejidad del body"""
        return self.visit(node.body)
    
    def visit_Program(self, node: Program) -> str:
        """Program: no tiene sentido calcular complejidad del programa completo"""
        return "N/A"
