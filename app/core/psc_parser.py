"""
Parser de pseudocódigo a IR usando Lark.
Convierte árbol Lark → nuestro IR (ast_nodes).
"""
from lark import Lark, Transformer, Token
from typing import List, Optional, Union
from pathlib import Path
from app.models.ast_nodes import (
    Program, Function, Param, Block, Stmt, Expr,
    Assign, Return, ExprStmt, If, While, For,
    Literal, Var, ArrayAccess, BinOp, UnOp, Compare, Call
)


# Cargar la gramática
GRAMMAR_PATH = Path(__file__).parent.parent / "grammar" / "pseudocode.lark"


class PseudocodeToIR(Transformer):
    """Transformer que convierte árbol Lark a IR"""
    
    # ========================================================================
    # PROGRAMA Y FUNCIONES
    # ========================================================================
    
    def start(self, items):
        """Punto de entrada: lista de statements (procedimientos)"""
        functions = []
        for item in items:
            if isinstance(item, Function):
                functions.append(item)
            # Ignorar None (declaraciones de variables)
        return Program(functions=functions)
    
    def statement(self, items):
        """Envuelve statement individual, filtrando None"""
        if items and items[0] is None:
            return None
        return items[0] if items else None
    
    def procedure_def(self, items):
        """Definición de procedimiento"""
        # items: [name, parameter_list (opcional), *body_statements]
        name = str(items[0])
        
        # Buscar parámetros y statements
        params = []
        body_items = []
        
        for item in items[1:]:
            if isinstance(item, list):
                # Lista de parámetros (resultado de parameter_list)
                params = item
            elif isinstance(item, Stmt):
                body_items.append(item)
            # Ignorar None (declaraciones de variables)
        
        body = Block(statements=body_items)
        return Function(name=name, params=params, body=body)
    
    def parameter_list(self, items):
        """Lista de parámetros"""
        return items
    
    def parameter(self, items):
        """Parámetro individual"""
        if len(items) == 1:
            return Param(name=str(items[0]))
        # TODO: manejar arrays y objetos como parámetros
        return Param(name=str(items[0]))
    
    # ========================================================================
    # SENTENCIAS
    # ========================================================================
    
    def var_declaration(self, items):
        """Declaración de variables: a, b, c"""
        # Simplemente ignoramos las declaraciones de variables
        # ya que no afectan el AST (solo las asignaciones importan)
        return None
    
    def statement(self, items):
        """Envuelve statement individual, filtrando None"""
        if items[0] is None:
            return None
        return items[0]
    
    def lvalue(self, items):
        """Left-hand side value: variable, array[index], or object.field"""
        if len(items) == 1:
            # Simple variable
            return Var(name=str(items[0]))
        elif len(items) == 2:
            # Array access: name[index]
            name = str(items[0])
            index = items[1]
            return ArrayAccess(array=Var(name=name), index=index)
        elif len(items) == 3:
            # Field access: name.field (no usado aún, pero preparado)
            obj_name = str(items[0])
            field_name = str(items[2])
            return Var(name=f"{obj_name}.{field_name}")  # Simplificación
        return items[0]
    
    def assignment(self, items):
        """Asignación: lvalue 🡨 expr"""
        target = items[0]  # Ya viene procesado por lvalue()
        value = items[1]
        return Assign(target=target, value=value)
    
    def return_statement(self, items):
        """Return statement"""
        if items:
            return Return(value=items[0])
        return Return(value=None)
    
    def call_statement(self, items):
        """CALL funcion(args)"""
        call_expr = items[0]
        return ExprStmt(expr=call_expr)
    
    def then_part(self, items):
        """Bloque then: puede ser begin...end o statement único"""
        # Filtrar None statements (declaraciones de variables)
        stmts = [item for item in items if item is not None and isinstance(item, Stmt)]
        return Block(statements=stmts)
    
    def else_part(self, items):
        """Bloque else: puede ser begin...end o statement único"""
        # Filtrar None statements (declaraciones de variables)
        stmts = [item for item in items if item is not None and isinstance(item, Stmt)]
        return Block(statements=stmts)
    
    def if_statement(self, items):
        """If-then-else - ahora con then_part y else_part como bloques"""
        condition = items[0]
        then_block = items[1]  # Ya es un Block gracias a then_part()
        else_block = items[2] if len(items) > 2 else None  # Block o None
        
        return If(cond=condition, then_block=then_block, else_block=else_block)
    
    def while_loop(self, items):
        """While loop"""
        condition = items[0]
        body_stmts = [item for item in items[1:] if isinstance(item, Stmt)]
        body = Block(statements=body_stmts)
        return While(cond=condition, body=body)
    
    def for_loop(self, items):
        """For loop: for var 🡨 start to end do begin ... end"""
        var_name = str(items[0])
        start_expr = items[1]
        end_expr = items[2]
        body_stmts = [item for item in items[3:] if isinstance(item, Stmt)]
        body = Block(statements=body_stmts)
        return For(var=var_name, start=start_expr, end=end_expr, body=body)
    
    def repeat_loop(self, items):
        """Repeat-until: convertir a while con lógica invertida"""
        # repeat ... until (condition) → while not (condition) do ...
        condition = items[-1]  # última es la condición
        body_stmts = [item for item in items[:-1] if isinstance(item, Stmt)]
        
        # Crear condición negada
        negated_cond = UnOp(op="not", operand=condition)
        body = Block(statements=body_stmts)
        
        return While(cond=negated_cond, body=body)
    
    # ========================================================================
    # EXPRESIONES
    # ========================================================================
    
    def number(self, items):
        """Número literal"""
        return Literal(value=float(items[0]) if '.' in str(items[0]) else int(items[0]))
    
    def variable(self, items):
        """Variable"""
        return Var(name=str(items[0]))
    
    def array_access(self, items):
        """Acceso a array: arr[index] o arr[i][j] (multi-dimensional)"""
        array_name = str(items[0])
        
        # Si hay múltiples índices, anidar ArrayAccess
        # arr[i][j] → ArrayAccess(ArrayAccess(Var(arr), i), j)
        result = Var(name=array_name)
        for index in items[1:]:
            result = ArrayAccess(array=result, index=index)
        
        return result
    
    def array_literal(self, items):
        """Array literal: [1, 2, 3]"""
        # Por ahora, representar como Call a una función especial "Array"
        # Alternativa: agregar ArrayLiteral al IR
        return Call(name="Array", args=items)
    
    def function_call(self, items):
        """Llamada a función"""
        func_name = str(items[0])
        args = [item for item in items[1:] if isinstance(item, Expr)]
        return Call(name=func_name, args=args)
    
    def true_value(self, items):
        """Valor True"""
        return Literal(value=True)
    
    def false_value(self, items):
        """Valor False"""
        return Literal(value=False)
    
    def null_value(self, items):
        """Valor NULL"""
        return Literal(value=None)
    
    def field_access(self, items):
        """Acceso a campo de objeto: obj.field"""
        # Por ahora simplificamos como variable compuesta
        obj_name = str(items[0])
        field_name = str(items[1])
        return Var(name=f"{obj_name}.{field_name}")
    
    # ========================================================================
    # OPERADORES
    # ========================================================================
    
    def or_expr(self, items):
        """Expresión OR"""
        if len(items) == 1:
            return items[0]
        # Reducir a binarios: a or b or c → (a or b) or c
        result = items[0]
        for item in items[1:]:
            result = BinOp(op="or", left=result, right=item)
        return result
    
    def and_expr(self, items):
        """Expresión AND"""
        if len(items) == 1:
            return items[0]
        result = items[0]
        for item in items[1:]:
            result = BinOp(op="and", left=result, right=item)
        return result
    
    def not_expr(self, items):
        """Expresión NOT"""
        if len(items) == 1:
            return items[0]
        # not not expr
        return UnOp(op="not", operand=items[0])
    
    def comparison(self, items):
        """Comparación"""
        if len(items) == 1:
            return items[0]
        
        # Mapear operadores de pseudocódigo a IR
        op_map = {
            "<": "<",
            ">": ">",
            "≤": "<=",
            "≥": ">=",
            "<=": "<=",
            ">=": ">=",
            "=": "=",
            "≠": "!=",
            "==": "=",
            "!=": "!="
        }
        
        left = items[0]
        op_token = items[1]
        right = items[2]
        
        # El operador ahora es un Token directamente
        op = str(op_token) if isinstance(op_token, Token) else str(op_token)
        
        return Compare(op=op_map.get(op, op), left=left, right=right)
    
    def arith_expr(self, items):
        """Expresión aritmética: suma/resta"""
        if len(items) == 1:
            return items[0]
        
        # Ahora con terminales: [term, PLUS/MINUS, term, PLUS/MINUS, term, ...]
        result = items[0]
        i = 1
        while i < len(items):
            if isinstance(items[i], Token):
                op = "+" if items[i].type in ["PLUS"] else "-"
                if i + 1 < len(items):
                    result = BinOp(op=op, left=result, right=items[i + 1])
                    i += 2
                else:
                    i += 1
            else:
                # Si no hay operador, asumir +
                result = BinOp(op="+", left=result, right=items[i])
                i += 1
        
        return result
    
    def term(self, items):
        """Término: multiplicación/división"""
        if len(items) == 1:
            return items[0]
        
        # Con terminales: [factor, STAR/SLASH/DIV/MOD, factor, ...]
        result = items[0]
        i = 1
        while i < len(items):
            if isinstance(items[i], Token):
                token_type = items[i].type
                op = "*" if token_type == "STAR" else "/" if token_type == "SLASH" else "div" if token_type == "DIV" else "mod"
                if i + 1 < len(items):
                    result = BinOp(op=op, left=result, right=items[i + 1])
                    i += 2
                else:
                    i += 1
            else:
                # Si no hay operador, asumir *
                result = BinOp(op="*", left=result, right=items[i])
                i += 1
        
        return result
    
    def ceiling(self, items):
        """Techo: ┌x┐"""
        return Call(name="ceiling", args=[items[0]])
    
    def floor(self, items):
        """Piso: └x┘"""
        return Call(name="floor", args=[items[0]])
    
    def argument_list(self, items):
        """Lista de argumentos"""
        return items
    
    def condition(self, items):
        """Condición (alias para expresión)"""
        return items[0]
    
    # ========================================================================
    # HELPERS
    # ========================================================================
    
    def action_statement(self, items):
        """Acción (statement vacío)"""
        return ExprStmt(expr=Literal(value=None))


class PseudocodeParser:
    """Parser de pseudocódigo a IR"""
    
    def __init__(self):
        """Inicializa el parser con la gramática"""
        with open(GRAMMAR_PATH, 'r', encoding='utf-8') as f:
            grammar = f.read()
        self.parser = Lark(grammar, start='start', parser='lalr')
        self.transformer = PseudocodeToIR()
    
    def build(self, code: str) -> Program:
        """
        Parsea pseudocódigo y construye Program IR.
        
        Args:
            code: Pseudocódigo fuente
            
        Returns:
            Program con lista de funciones
            
        Raises:
            Exception: Si hay errores de parsing
        """
        try:
            tree = self.parser.parse(code)
            program = self.transformer.transform(tree)
            return program
        except Exception as e:
            raise Exception(f"Error parsing pseudocode: {str(e)}")
