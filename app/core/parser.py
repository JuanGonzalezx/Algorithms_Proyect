from lark import Lark, Transformer, Tree
from lark.exceptions import ParseError, LarkError
from typing import Optional, Dict, Any
import os
from app.models.ast_nodes import *
from app.models.schemas import ASTNode as SchemaASTNode
import logging

logger = logging.getLogger(__name__)

class PseudocodeParser:
    """Parser de pseudocódigo usando Lark"""
    
    def __init__(self):
        """Inicializa el parser con la gramática"""
        grammar_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 'grammar', 'pseudocode.lark'
        )
        
        try:
            with open(grammar_path, 'r', encoding='utf-8') as f:
                grammar = f.read()
            
            self.parser = Lark(
                grammar,
                parser='earley',  # Parser más robusto para gramáticas complejas
                debug=False
            )
            
            self.transformer = ASTTransformer()
            
        except FileNotFoundError:
            logger.error(f"Archivo de gramática no encontrado: {grammar_path}")
            raise
        except Exception as e:
            logger.error(f"Error al inicializar parser: {e}")
            raise
    
    def parse(self, pseudocode: str) -> tuple[bool, Optional[Program], Optional[str]]:
        """
        Parsea pseudocódigo y retorna el AST
        
        Args:
            pseudocode: Código a parsear
            
        Returns:
            tuple: (success, ast_root, error_message)
        """
        try:
            # Parsear con Lark
            tree = self.parser.parse(pseudocode)
            
            # Transformar a AST
            ast_root = self.transformer.transform(tree)
            
            return True, ast_root, None
            
        except ParseError as e:
            error_msg = f"Error de sintaxis en línea {e.line}, columna {e.column}: {e}"
            logger.warning(f"Parse error: {error_msg}")
            return False, None, error_msg
            
        except LarkError as e:
            error_msg = f"Error del parser: {str(e)}"
            logger.warning(f"Lark error: {error_msg}")
            return False, None, error_msg
            
        except Exception as e:
            error_msg = f"Error inesperado durante el parsing: {str(e)}"
            logger.error(f"Unexpected error: {error_msg}")
            return False, None, error_msg
    
    def validate_syntax(self, pseudocode: str) -> tuple[bool, Optional[str]]:
        """
        Valida únicamente la sintaxis sin generar AST
        
        Args:
            pseudocode: Código a validar
            
        Returns:
            tuple: (is_valid, error_message)
        """
        success, _, error = self.parse(pseudocode)
        return success, error


class ASTTransformer(Transformer):
    """Transformador que convierte el parse tree de Lark a nuestro AST"""
    
    def start(self, statements):
        """Raíz del programa"""
        program = Program()
        program.children = list(statements)
        return program
    
    def procedure_def(self, items):
        """Definición de procedimiento"""
        name = str(items[0])
        
        # Extraer parámetros si existen
        params = []
        body = []
        
        for item in items[1:]:
            if isinstance(item, list) and len(item) > 0 and isinstance(item[0], str):
                # Es lista de parámetros
                params = [str(p) for p in item]
            elif isinstance(item, ASTNode):
                # Es parte del cuerpo
                body.append(item)
        
        procedure = Procedure(name=name, parameters=params)
        procedure.children = body
        return procedure
    
    def parameter_list(self, params):
        """Lista de parámetros"""
        return [str(p) for p in params]
    
    def parameter(self, items):
        """Parámetro individual"""
        return str(items[0])
    
    def for_loop(self, items):
        """Bucle for"""
        variable = str(items[0])
        start_expr = items[1]
        end_expr = items[2]
        body = list(items[3:])
        
        for_node = ForLoop(variable=variable, start_expr=start_expr, end_expr=end_expr)
        for_node.children = body
        return for_node
    
    def while_loop(self, items):
        """Bucle while"""
        condition = items[0]
        body = list(items[1:])
        
        while_node = WhileLoop(condition=condition)
        while_node.children = body
        return while_node
    
    def if_statement(self, items):
        """Condicional if"""
        condition = items[0]
        
        # Separar then_body y else_body
        then_body = []
        else_body = []
        in_else = False
        
        for i, item in enumerate(items[1:], 1):
            if isinstance(item, str) and item == "else":
                in_else = True
                continue
            
            if in_else:
                else_body.append(item)
            else:
                then_body.append(item)
        
        if_node = IfStatement(condition=condition, then_body=then_body, else_body=else_body)
        return if_node
    
    def assignment(self, items):
        """Asignación"""
        target = str(items[0])
        expression = items[1] if len(items) > 1 else None
        
        return Assignment(target=target, expression=expression)
    
    def call_statement(self, items):
        """Llamada a función"""
        function_name = str(items[0])
        arguments = list(items[1:]) if len(items) > 1 else []
        
        return FunctionCall(function_name=function_name, arguments=arguments)
    
    def variable(self, items):
        """Variable"""
        return Variable(name=str(items[0]))
    
    def number(self, items):
        """Número"""
        return Number(value=int(items[0]))
    
    def action_statement(self, items):
        """Acción genérica"""
        action = ASTNode(node_type="action", value="accion")
        return action

    # Operadores y expresiones
    def arith_expr(self, items):
        """Expresión aritmética"""
        if len(items) == 1:
            return items[0]
        
        # Construir árbol de expresión binaria
        left = items[0]
        for i in range(1, len(items), 2):
            operator = str(items[i])
            right = items[i + 1]
            
            expr = Expression(operator=operator, left=left, right=right)
            left = expr
        
        return left
    
    def term(self, items):
        """Término"""
        return self.arith_expr(items)
    
    def factor(self, items):
        """Factor"""
        return items[0]
    
    # Valores por defecto para reglas no implementadas
    def __default__(self, data, children, meta):
        """Manejo por defecto de reglas no implementadas"""
        if len(children) == 1:
            return children[0]
        return children


# Instancia global del parser
pseudocode_parser = PseudocodeParser()