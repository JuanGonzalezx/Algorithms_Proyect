"""
Parser Agent - Convierte Lark parse tree a AST custom
Usa la misma gramática que syntax_validator pero genera AST tipado.
"""
from pathlib import Path
from typing import Optional, List, Union
from lark import Lark, Transformer, Tree, Token, v_args
from app.models.ast_nodes import (
    Program, Function, Param, Block,
    Assign, If, While, For, Return, ExprStmt,
    Var, Literal, BinOp, UnOp, Compare, Call, ArrayAccess,
    Expr, Stmt
)


class PseudocodeToASTTransformer(Transformer):
    """
    Transforma el parse tree de Lark a nuestro AST custom.
    Cada método corresponde a una regla de la gramática.
    """
    
    def _get_line_info(self, children):
        """
        Extrae información de línea de los children (tokens/trees).
        
        Returns:
            tuple: (line_start, line_end) o (None, None) si no hay info
        """
        line_start = None
        line_end = None
        
        def extract_from_item(item):
            nonlocal line_start, line_end
            
            if isinstance(item, Token):
                if hasattr(item, 'line'):
                    if line_start is None or item.line < line_start:
                        line_start = item.line
                if hasattr(item, 'end_line'):
                    if line_end is None or item.end_line > line_end:
                        line_end = item.end_line
            elif isinstance(item, Tree):
                if hasattr(item, 'meta'):
                    if hasattr(item.meta, 'line'):
                        if line_start is None or item.meta.line < line_start:
                            line_start = item.meta.line
                    if hasattr(item.meta, 'end_line'):
                        if line_end is None or item.meta.end_line > line_end:
                            line_end = item.meta.end_line
                # Recursively check children of Tree
                if hasattr(item, 'children'):
                    for child in item.children:
                        extract_from_item(child)
        
        for child in children:
            extract_from_item(child)
        
        return line_start, line_end
    
    # ======== PROGRAMA Y FUNCIONES ========
    
    def start(self, children):
        """start: statement+"""
        # El start contiene statements, que pueden incluir procedure_def
        # Los statements que son funciones se extraen aquí
        functions = []
        for child in children:
            if isinstance(child, Function):
                functions.append(child)
        return Program(functions=functions)
    
    def statement(self, children):
        """statement: procedure_def | var_declaration | for_loop | while_loop | ..."""
        # Statement es un wrapper, retornar el contenido directamente
        return children[0]
    
    def procedure_def(self, children):
        """procedure_def: "procedimiento" NAME "(" [parameter_list] ")" "begin" statement* "end"
                        | NAME "(" [parameter_list] ")" "begin" statement* "end" """
        # children: [NAME, [params]?, statement*]
        name = str(children[0])  # Primer elemento siempre es NAME
        
        # Buscar parámetros (lista) y statements
        params = []
        statements = []
        
        for child in children[1:]:
            if isinstance(child, list):
                params = child
            elif isinstance(child, Stmt):
                statements.append(child)
        
        body = Block(statements=statements)
        return Function(name=name, params=params, body=body)
    
    def parameter_list(self, children):
        """parameter_list: parameter ("," parameter)*"""
        return children  # Los parámetros ya están procesados
    
    def parameter(self, children):
        """parameter: NAME ["[" array_range "]"] | "Clase" NAME"""
        # Por simplicidad, solo tomamos el NAME
        name = None
        for child in children:
            if isinstance(child, Token) and child.type == "NAME":
                name = str(child)
                break
        return Param(name=name or "")
    
    # ======== SENTENCIAS ========
    
    @v_args(meta=True)
    def assignment(self, meta, children):
        """assignment: lvalue "🡨" expression"""
        target = children[0]  # lvalue (puede ser Var, ArrayAccess, etc.)
        value = children[1]  # expression
        
        line_start = meta.line if hasattr(meta, 'line') else None
        line_end = meta.end_line if hasattr(meta, 'end_line') else None
        return Assign(target=target, value=value, line_start=line_start, line_end=line_end)
    
    def lvalue(self, children):
        """lvalue: NAME ["[" expression "]"] | NAME "." NAME"""
        if len(children) == 1:
            # NAME simple
            return Var(name=str(children[0]))
        elif len(children) == 2:
            # NAME "[" expression "]" o NAME "." NAME
            name = str(children[0])
            if isinstance(children[1], Expr):
                # Array access
                return ArrayAccess(array=Var(name=name), index=children[1])
            else:
                # Field access - por ahora lo manejamos como Var
                field_name = str(children[1])
                return Var(name=f"{name}.{field_name}")
        return Var(name="")
    
    @v_args(meta=True)
    def if_statement(self, meta, children):
        """if_statement: "if" condition "then" then_part ["else" else_part]"""
        cond = children[0]  # condition
        then_block = children[1]  # then_part (ya es Block)
        else_block = children[2] if len(children) > 2 else None  # else_part (Block o None)
        
        line_start = meta.line if hasattr(meta, 'line') else None
        line_end = meta.end_line if hasattr(meta, 'end_line') else None
        return If(cond=cond, then_block=then_block, else_block=else_block, 
                  line_start=line_start, line_end=line_end)
    
    def then_part(self, children):
        """then_part: "begin" statement* "end" | statement"""
        if len(children) == 1 and isinstance(children[0], Stmt):
            # Un solo statement sin begin/end
            return Block(statements=[children[0]])
        else:
            # Múltiples statements con begin/end
            statements = [child for child in children if isinstance(child, Stmt)]
            return Block(statements=statements)
    
    def else_part(self, children):
        """else_part: "begin" statement* "end" | statement"""
        if len(children) == 1 and isinstance(children[0], Stmt):
            return Block(statements=[children[0]])
        else:
            statements = [child for child in children if isinstance(child, Stmt)]
            return Block(statements=statements)
    
    @v_args(meta=True)
    def while_loop(self, meta, children):
        """while_loop: "while" condition "do" "begin" statement* "end" """
        cond = children[0]  # condition/expression
        
        # Resto son statements del body
        statements = [child for child in children[1:] if isinstance(child, Stmt)]
        body = Block(statements=statements)
        
        line_start = meta.line if hasattr(meta, 'line') else None
        line_end = meta.end_line if hasattr(meta, 'end_line') else None
        return While(cond=cond, body=body, line_start=line_start, line_end=line_end)
    
    @v_args(meta=True)
    def for_loop(self, meta, children):
        """for_loop: "for" NAME "🡨" expression "to" expression "do" "begin" statement* "end" """
        var_name = str(children[0])  # Token NAME
        start = children[1]  # expression (start)
        end = children[2]  # expression (end)
        
        # Statements del body
        statements = [child for child in children[3:] if isinstance(child, Stmt)]
        body = Block(statements=statements)
        
        line_start = meta.line if hasattr(meta, 'line') else None
        line_end = meta.end_line if hasattr(meta, 'end_line') else None
        return For(var=var_name, start=start, end=end, body=body, 
                   line_start=line_start, line_end=line_end)
    
    def repeat_loop(self, children):
        """repeat_loop: "repetir" block "hasta" "que" expr"""
        # Convertir repeat-until a while (not cond)
        body = children[0]
        cond = children[1]
        
        # repeat-until se ejecuta al menos una vez, pero para análisis
        # lo tratamos como while con condición negada
        negated_cond = UnOp(op="not", operand=cond)
        return While(cond=negated_cond, body=body)
    
    @v_args(meta=True)
    def return_statement(self, meta, children):
        """return_statement: "retornar" expr?"""
        value = children[0] if children else None
        line_start = meta.line if hasattr(meta, 'line') else None
        line_end = meta.end_line if hasattr(meta, 'end_line') else None
        return Return(value=value, line_start=line_start, line_end=line_end)
    
    def expr_stmt(self, children):
        """expr_stmt: expr"""
        return ExprStmt(expr=children[0])
    
    # ======== EXPRESIONES ========
    
    def expr(self, children):
        """expr: or_expr"""
        return children[0]
    
    def or_expr(self, children):
        """or_expr: and_expr ("o" and_expr)*"""
        if len(children) == 1:
            return children[0]
        
        # Construir árbol binario izquierda-asociativo
        result = children[0]
        for i in range(1, len(children)):
            child = children[i]
            # Filtrar tokens "or"/"o" que puedan venir mezclados
            if isinstance(child, Token):
                continue
            result = BinOp(op="or", left=result, right=child)
        return result
    
    def and_expr(self, children):
        """and_expr: not_expr ("y" not_expr)*"""
        if len(children) == 1:
            return children[0]
        
        result = children[0]
        for i in range(1, len(children)):
            child = children[i]
            # Filtrar tokens "and"/"y" que puedan venir mezclados
            if isinstance(child, Token):
                continue
            result = BinOp(op="and", left=result, right=child)
        return result
    
    def not_expr(self, children):
        """not_expr: "no" not_expr | comparison"""
        if len(children) == 2:  # "no" expr
            return UnOp(op="not", operand=children[1])
        return children[0]
    
    def comparison(self, children):
        """comparison: arith_expr [(LESSTHAN | MORETHAN | LEQ | GEQ | EQUAL | NOTEQUAL) arith_expr] 
                      | arith_expr"""
        if len(children) == 1:
            return children[0]
        
        left = children[0]
        op_token = children[1]  # Token
        right = children[2]
        
        # Extraer operador del token
        op = str(op_token)
        
        # Normalizar operadores
        op_map = {
            "=": "==",
            "==": "==",
            "≠": "!=",
            "!=": "!=",
            "<>": "!=",
            "≤": "<=",
            "<=": "<=",
            "≥": ">=",
            ">=": ">="
        }
        op = op_map.get(op, op)
        
        return Compare(op=op, left=left, right=right)
    
    def arith_expr(self, children):
        """arith_expr: term ((PLUS|MINUS) term)*"""
        if len(children) == 1:
            return children[0]
        
        result = children[0]
        i = 1
        while i < len(children):
            op = str(children[i])  # Token PLUS o MINUS
            right = children[i + 1]
            result = BinOp(op=op, left=result, right=right)
            i += 2
        return result
    
    def term(self, children):
        """term: factor ((STAR|SLASH|MOD|DIV) factor)*"""
        if len(children) == 1:
            return children[0]
        
        result = children[0]
        i = 1
        while i < len(children):
            op = str(children[i])  # Token
            right = children[i + 1]
            result = BinOp(op=op, left=result, right=right)
            i += 2
        return result
    
    def condition(self, children):
        """condition: expression"""
        return children[0]
    
    # Procesadores de terminals y expresiones atómicas
    
    def number(self, children):
        """NUMBER terminal"""
        val = str(children[0])
        return Literal(value=int(val) if '.' not in val else float(val))
    
    def variable(self, children):
        """NAME terminal como variable"""
        return Var(name=str(children[0]))
    
    def function_call(self, children):
        """function_call: NAME "(" [argument_list] ")" """
        name = str(children[0])
        # argument_list retorna lista de expresiones
        args = children[1] if len(children) > 1 and isinstance(children[1], list) else []
        return Call(name=name, args=args)
    
    def argument_list(self, children):
        """argument_list: expression ("," expression)*"""
        return children  # Ya son expresiones procesadas
    
    def array_access(self, children):
        """array_access: NAME "[" expression "]" ("[" expression "]")* """
        array_name = str(children[0])
        index = children[1]  # Primera dimensión
        
        # Si hay más dimensiones, anidar ArrayAccess
        result = ArrayAccess(array=Var(name=array_name), index=index)
        for extra_index in children[2:]:
            if isinstance(extra_index, Expr):
                # Convertir a nested access: arr[i][j] → ArrayAccess(ArrayAccess(arr, i), j)
                result = ArrayAccess(array=result, index=extra_index)
        
        return result
    
    def field_access(self, children):
        """field_access: NAME "." NAME"""
        # Por ahora, representarlo como Var con nombre compuesto
        obj_name = str(children[0])
        field_name = str(children[1])
        return Var(name=f"{obj_name}.{field_name}")


class ParserAgent:
    """
    Agente Parser: Convierte pseudocódigo a AST custom.
    
    Flujo:
    1. Pseudocódigo → Lark parse tree (usando grammar.lark)
    2. Parse tree → AST custom (usando Transformer)
    
    Este agente reutiliza la misma gramática que syntax_validator
    pero genera una estructura AST tipada lista para análisis.
    """
    
    def __init__(self):
        """Inicializa el parser con la gramática compartida."""
        self.grammar_path = Path(__file__).parent.parent.parent / "shared" / "grammar" / "grammar.lark"
        self.parser = None
        self.transformer = PseudocodeToASTTransformer()
        self._load_grammar()
    
    def _load_grammar(self):
        """Carga la gramática Lark desde el archivo compartido."""
        if not self.grammar_path.exists():
            raise FileNotFoundError(f"Gramática no encontrada: {self.grammar_path}")
        
        with open(self.grammar_path, "r", encoding="utf-8") as f:
            grammar = f.read()
        
        self.parser = Lark(
            grammar,
            start="start",
            parser="lalr",
            propagate_positions=True,  # Para debugging
            maybe_placeholders=False
        )
    
    def parse(self, pseudocode: str) -> Program:
        """
        Convierte pseudocódigo a AST custom.
        
        Args:
            pseudocode: Código fuente en pseudocódigo
            
        Returns:
            Program: AST raíz con todas las funciones
            
        Raises:
            Exception: Si hay error de parsing o transformación
        """
        # Paso 1: Parse pseudocódigo a parse tree de Lark
        parse_tree = self.parser.parse(pseudocode)
        
        # Paso 2: Transformar parse tree a AST custom
        ast = self.transformer.transform(parse_tree)
        
        return ast
    
    def __call__(self, input_data: dict) -> dict:
        """
        Interfaz compatible con LangGraph.
        
        Args:
            input_data: {"pseudocode": "..."}
            
        Returns:
            {"ast": Program, "success": bool, "error": Optional[str]}
        """
        try:
            pseudocode = input_data.get("pseudocode", "")
            ast = self.parse(pseudocode)
            
            return {
                "ast": ast,
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "ast": None,
                "success": False,
                "error": str(e)
            }


# Singleton global
_parser_agent = None

def get_parser_agent() -> ParserAgent:
    """Retorna instancia singleton del parser agent."""
    global _parser_agent
    if _parser_agent is None:
        _parser_agent = ParserAgent()
    return _parser_agent
