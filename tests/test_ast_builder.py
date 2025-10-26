"""
Tests para el constructor de AST Python → IR.
"""
import pytest
from app.core.py_ast_builder import PythonToIR
from app.models.ast_nodes import Program, Function, For, While, If, Assign, Return


class TestPythonToIR:
    """Tests para PythonToIR builder"""
    
    def test_sum_array_with_for(self):
        """Test: suma de arreglo con for"""
        code = """
def sum_array(arr, n):
    suma = 0
    for i in range(n):
        suma += arr[i]
    return suma
"""
        builder = PythonToIR()
        program = builder.build(code)
        
        assert isinstance(program, Program)
        assert len(program.functions) == 1
        
        func = program.functions[0]
        assert func.name == "sum_array"
        assert len(func.params) == 2
        assert func.params[0].name == "arr"
        assert func.params[1].name == "n"
        
        # Verificar estructura del body
        stmts = func.body.statements
        assert len(stmts) == 3  # assign, for, return
        
        # Primera statement: suma = 0
        assert isinstance(stmts[0], Assign)
        assert stmts[0].target.name == "suma"
        
        # Segunda statement: for loop
        assert isinstance(stmts[1], For)
        assert stmts[1].var == "i"
        
        # Tercera statement: return
        assert isinstance(stmts[2], Return)
    
    def test_binary_search_with_while_if(self):
        """Test: búsqueda binaria con while y if"""
        code = """
def binary_search(arr, target):
    left = 0
    right = len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        else:
            if arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
    
    return -1
"""
        builder = PythonToIR()
        program = builder.build(code)
        
        assert isinstance(program, Program)
        assert len(program.functions) == 1
        
        func = program.functions[0]
        assert func.name == "binary_search"
        assert len(func.params) == 2
        
        stmts = func.body.statements
        # left = 0, right = ..., while, return -1
        assert len(stmts) == 4
        
        # Verificar while loop
        while_stmt = stmts[2]
        assert isinstance(while_stmt, While)
        
        # Verificar if dentro del while
        while_body = while_stmt.body.statements
        assert len(while_body) == 2  # mid = ..., if
        assert isinstance(while_body[1], If)
        
        # Verificar if anidado en el else
        outer_if = while_body[1]
        assert outer_if.else_block is not None
        assert len(outer_if.else_block.statements) == 1
        assert isinstance(outer_if.else_block.statements[0], If)
    
    def test_factorial_recursive(self):
        """Test: factorial recursivo"""
        code = """
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)
"""
        builder = PythonToIR()
        program = builder.build(code)
        
        assert isinstance(program, Program)
        assert len(program.functions) == 1
        
        func = program.functions[0]
        assert func.name == "factorial"
        assert len(func.params) == 1
        assert func.params[0].name == "n"
        
        stmts = func.body.statements
        assert len(stmts) == 1
        assert isinstance(stmts[0], If)
        
        if_stmt = stmts[0]
        # Then: return 1
        assert len(if_stmt.then_block.statements) == 1
        assert isinstance(if_stmt.then_block.statements[0], Return)
        
        # Else: return n * factorial(n-1)
        assert if_stmt.else_block is not None
        assert len(if_stmt.else_block.statements) == 1
        assert isinstance(if_stmt.else_block.statements[0], Return)
    
    def test_unsupported_range_with_step(self):
        """Test: range con step debe fallar"""
        code = """
def test():
    for i in range(1, 10, 2):
        pass
"""
        builder = PythonToIR()
        with pytest.raises(NotImplementedError, match="step not supported"):
            builder.build(code)
    
    def test_unsupported_chained_comparison(self):
        """Test: comparaciones encadenadas deben fallar"""
        code = """
def test(a, b, c):
    if a < b < c:
        return True
"""
        builder = PythonToIR()
        with pytest.raises(NotImplementedError, match="Chained comparison"):
            builder.build(code)
    
    def test_invalid_python_syntax(self):
        """Test: sintaxis Python inválida debe fallar"""
        code = "def test(\n  invalid syntax"
        builder = PythonToIR()
        with pytest.raises(SyntaxError):
            builder.build(code)
    
    def test_unsupported_tuple_unpacking(self):
        """Test: tuple unpacking en asignación debe fallar"""
        code = """
def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]
"""
        builder = PythonToIR()
        with pytest.raises(NotImplementedError, match="Assignment target Tuple"):
            builder.build(code)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
