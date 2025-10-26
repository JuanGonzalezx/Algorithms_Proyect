"""
Constructor de IR desde código Python usando el módulo ast estándar.
Convierte Python AST → nuestro IR (ast_nodes).
"""
import ast
from typing import List, Union, Any
from app.models.ast_nodes import (
    Program, Function, Param, Block, Stmt, Expr,
    Assign, Return, ExprStmt, If, While, For,
    Literal, Var, ArrayAccess, BinOp, UnOp, Compare, Call
)


class PythonToIR:
    """Convierte código Python a nuestro IR"""
    
    def build(self, code: str) -> Program:
        """
        Parsea código Python y construye Program IR.
        
        Args:
            code: Código Python fuente
            
        Returns:
            Program con lista de funciones
            
        Raises:
            SyntaxError: Si el código Python es inválido
            NotImplementedError: Si usa características no soportadas
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise SyntaxError(f"Invalid Python syntax: {e}")
        
        functions = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                functions.append(self._build_function(node))
            else:
                raise NotImplementedError(
                    f"Top-level {node.__class__.__name__} not supported. "
                    f"Only function definitions allowed at module level."
                )
        
        return Program(functions=functions)
    
    def _build_function(self, node: ast.FunctionDef) -> Function:
        """Construye Function desde ast.FunctionDef"""
        params = []
        for arg in node.args.args:
            params.append(Param(name=arg.arg))
        
        # Validar que no tenga características complejas
        if node.args.vararg or node.args.kwarg or node.args.kwonlyargs:
            raise NotImplementedError(
                f"Function '{node.name}': *args, **kwargs, and keyword-only args not supported"
            )
        
        if node.decorator_list:
            raise NotImplementedError(
                f"Function '{node.name}': decorators not supported"
            )
        
        body = self._build_block(node.body)
        
        return Function(
            name=node.name,
            params=params,
            body=body,
            line=node.lineno,
            col=node.col_offset
        )
    
    def _build_block(self, stmts: List[ast.stmt]) -> Block:
        """Construye Block desde lista de statements"""
        statements = []
        for stmt in stmts:
            statements.append(self._build_stmt(stmt))
        return Block(statements=statements)
    
    def _build_stmt(self, node: ast.stmt) -> Stmt:
        """Construye Stmt desde ast.stmt"""
        if isinstance(node, ast.Assign):
            return self._build_assign(node)
        elif isinstance(node, ast.AugAssign):
            return self._build_aug_assign(node)
        elif isinstance(node, ast.Return):
            return self._build_return(node)
        elif isinstance(node, ast.If):
            return self._build_if(node)
        elif isinstance(node, ast.While):
            return self._build_while(node)
        elif isinstance(node, ast.For):
            return self._build_for(node)
        elif isinstance(node, ast.Expr):
            return ExprStmt(
                expr=self._build_expr(node.value),
                line=node.lineno,
                col=node.col_offset
            )
        else:
            raise NotImplementedError(
                f"Statement {node.__class__.__name__} at line {node.lineno} not supported"
            )
    
    def _build_assign(self, node: ast.Assign) -> Assign:
        """Construye Assign desde ast.Assign"""
        if len(node.targets) > 1:
            raise NotImplementedError(
                f"Multiple assignment targets (a=b=c) at line {node.lineno} not supported"
            )
        
        target = node.targets[0]
        target_ir = self._build_lvalue(target)
        value_ir = self._build_expr(node.value)
        
        return Assign(
            target=target_ir,
            value=value_ir,
            line=node.lineno,
            col=node.col_offset
        )
    
    def _build_aug_assign(self, node: ast.AugAssign) -> Assign:
        """Construye Assign desde ast.AugAssign (ej: x += 1)"""
        target_ir = self._build_lvalue(node.target)
        
        # Convertir x += 1 a x = x + 1
        op_map = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.FloorDiv: "div",
            ast.Mod: "mod"
        }
        
        op_type = type(node.op)
        if op_type not in op_map:
            raise NotImplementedError(
                f"Augmented assignment operator {node.op.__class__.__name__} "
                f"at line {node.lineno} not supported"
            )
        
        # Crear BinOp: target = target op value
        bin_op = BinOp(
            op=op_map[op_type],
            left=self._build_expr(node.target),
            right=self._build_expr(node.value),
            line=node.lineno,
            col=node.col_offset
        )
        
        return Assign(
            target=target_ir,
            value=bin_op,
            line=node.lineno,
            col=node.col_offset
        )
    
    def _build_lvalue(self, node: ast.expr) -> Union[Var, ArrayAccess]:
        """Construye target de asignación (lvalue)"""
        if isinstance(node, ast.Name):
            return Var(name=node.id, line=node.lineno, col=node.col_offset)
        elif isinstance(node, ast.Subscript):
            return self._build_array_access(node)
        else:
            raise NotImplementedError(
                f"Assignment target {node.__class__.__name__} at line {node.lineno} not supported"
            )
    
    def _build_return(self, node: ast.Return) -> Return:
        """Construye Return desde ast.Return"""
        value = self._build_expr(node.value) if node.value else None
        return Return(value=value, line=node.lineno, col=node.col_offset)
    
    def _build_if(self, node: ast.If) -> If:
        """Construye If desde ast.If"""
        cond = self._build_expr(node.test)
        then_block = self._build_block(node.body)
        else_block = self._build_block(node.orelse) if node.orelse else None
        
        return If(
            cond=cond,
            then_block=then_block,
            else_block=else_block,
            line=node.lineno,
            col=node.col_offset
        )
    
    def _build_while(self, node: ast.While) -> While:
        """Construye While desde ast.While"""
        cond = self._build_expr(node.test)
        body = self._build_block(node.body)
        
        if node.orelse:
            raise NotImplementedError(
                f"While-else at line {node.lineno} not supported"
            )
        
        return While(
            cond=cond,
            body=body,
            line=node.lineno,
            col=node.col_offset
        )
    
    def _build_for(self, node: ast.For) -> For:
        """Construye For desde ast.For (solo range)"""
        if node.orelse:
            raise NotImplementedError(
                f"For-else at line {node.lineno} not supported"
            )
        
        if not isinstance(node.target, ast.Name):
            raise NotImplementedError(
                f"For loop with non-simple target at line {node.lineno} not supported"
            )
        
        var_name = node.target.id
        
        # Validar que sea range()
        if not isinstance(node.iter, ast.Call):
            raise NotImplementedError(
                f"For loop at line {node.lineno} must use range(). "
                f"Iterating over {node.iter.__class__.__name__} not supported"
            )
        
        call = node.iter
        if not isinstance(call.func, ast.Name) or call.func.id != "range":
            raise NotImplementedError(
                f"For loop at line {node.lineno} must use range(). "
                f"Other iterables not supported"
            )
        
        # Parse range(start, end) o range(end)
        if len(call.args) == 1:
            start = Literal(value=0)
            end = self._build_expr(call.args[0])
        elif len(call.args) == 2:
            start = self._build_expr(call.args[0])
            end = self._build_expr(call.args[1])
        elif len(call.args) == 3:
            raise NotImplementedError(
                f"For loop at line {node.lineno}: range() with step not supported"
            )
        else:
            raise NotImplementedError(
                f"For loop at line {node.lineno}: range() with {len(call.args)} args not supported"
            )
        
        if call.keywords:
            raise NotImplementedError(
                f"For loop at line {node.lineno}: range() with keyword args not supported"
            )
        
        body = self._build_block(node.body)
        
        return For(
            var=var_name,
            start=start,
            end=end,
            body=body,
            line=node.lineno,
            col=node.col_offset
        )
    
    def _build_expr(self, node: ast.expr) -> Expr:
        """Construye Expr desde ast.expr"""
        if isinstance(node, ast.Constant):
            return Literal(value=node.value, line=node.lineno, col=node.col_offset)
        elif isinstance(node, ast.Num):  # Python 3.7 compat
            return Literal(value=node.n, line=node.lineno, col=node.col_offset)
        elif isinstance(node, ast.Name):
            return Var(name=node.id, line=node.lineno, col=node.col_offset)
        elif isinstance(node, ast.Subscript):
            return self._build_array_access(node)
        elif isinstance(node, ast.BinOp):
            return self._build_binop(node)
        elif isinstance(node, ast.UnaryOp):
            return self._build_unop(node)
        elif isinstance(node, ast.Compare):
            return self._build_compare(node)
        elif isinstance(node, ast.Call):
            return self._build_call(node)
        elif isinstance(node, ast.BoolOp):
            return self._build_boolop(node)
        else:
            raise NotImplementedError(
                f"Expression {node.__class__.__name__} at line {node.lineno} not supported"
            )
    
    def _build_array_access(self, node: ast.Subscript) -> ArrayAccess:
        """Construye ArrayAccess desde ast.Subscript"""
        if not isinstance(node.value, ast.Name):
            raise NotImplementedError(
                f"Complex array access at line {node.lineno} not supported. "
                f"Only simple names like arr[i]"
            )
        
        array = Var(name=node.value.id, line=node.value.lineno, col=node.value.col_offset)
        
        # node.slice puede ser ast.Index (Python <3.9) o directamente la expresión (>=3.9)
        if hasattr(node.slice, 'value'):  # Python <3.9
            index = self._build_expr(node.slice.value)
        else:
            index = self._build_expr(node.slice)
        
        return ArrayAccess(
            array=array,
            index=index,
            line=node.lineno,
            col=node.col_offset
        )
    
    def _build_binop(self, node: ast.BinOp) -> BinOp:
        """Construye BinOp desde ast.BinOp"""
        op_map = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.FloorDiv: "div",
            ast.Mod: "mod"
        }
        
        op_type = type(node.op)
        if op_type not in op_map:
            raise NotImplementedError(
                f"Binary operator {node.op.__class__.__name__} at line {node.lineno} not supported"
            )
        
        return BinOp(
            op=op_map[op_type],
            left=self._build_expr(node.left),
            right=self._build_expr(node.right),
            line=node.lineno,
            col=node.col_offset
        )
    
    def _build_unop(self, node: ast.UnaryOp) -> UnOp:
        """Construye UnOp desde ast.UnaryOp"""
        op_map = {
            ast.USub: "-",
            ast.Not: "not"
        }
        
        op_type = type(node.op)
        if op_type not in op_map:
            raise NotImplementedError(
                f"Unary operator {node.op.__class__.__name__} at line {node.lineno} not supported"
            )
        
        return UnOp(
            op=op_map[op_type],
            operand=self._build_expr(node.operand),
            line=node.lineno,
            col=node.col_offset
        )
    
    def _build_compare(self, node: ast.Compare) -> Compare:
        """Construye Compare desde ast.Compare"""
        if len(node.ops) > 1:
            raise NotImplementedError(
                f"Chained comparison at line {node.lineno} not supported (a < b < c)"
            )
        
        op_map = {
            ast.Eq: "=",
            ast.NotEq: "!=",
            ast.Lt: "<",
            ast.LtE: "<=",
            ast.Gt: ">",
            ast.GtE: ">="
        }
        
        op_type = type(node.ops[0])
        if op_type not in op_map:
            raise NotImplementedError(
                f"Comparison operator {node.ops[0].__class__.__name__} "
                f"at line {node.lineno} not supported"
            )
        
        return Compare(
            op=op_map[op_type],
            left=self._build_expr(node.left),
            right=self._build_expr(node.comparators[0]),
            line=node.lineno,
            col=node.col_offset
        )
    
    def _build_boolop(self, node: ast.BoolOp) -> BinOp:
        """Construye BinOp desde ast.BoolOp (and/or)"""
        op_map = {
            ast.And: "and",
            ast.Or: "or"
        }
        
        op_type = type(node.op)
        if op_type not in op_map:
            raise NotImplementedError(
                f"Boolean operator {node.op.__class__.__name__} at line {node.lineno} not supported"
            )
        
        # Reducir múltiples operandos a binarios anidados: a and b and c -> (a and b) and c
        result = self._build_expr(node.values[0])
        for val in node.values[1:]:
            result = BinOp(
                op=op_map[op_type],
                left=result,
                right=self._build_expr(val),
                line=node.lineno,
                col=node.col_offset
            )
        
        return result
    
    def _build_call(self, node: ast.Call) -> Call:
        """Construye Call desde ast.Call"""
        if not isinstance(node.func, ast.Name):
            raise NotImplementedError(
                f"Call at line {node.lineno}: only simple function names supported. "
                f"Qualified names (module.func) not supported"
            )
        
        if node.keywords:
            raise NotImplementedError(
                f"Call at line {node.lineno}: keyword arguments not supported"
            )
        
        name = node.func.id
        args = [self._build_expr(arg) for arg in node.args]
        
        return Call(
            name=name,
            args=args,
            line=node.lineno,
            col=node.col_offset
        )
