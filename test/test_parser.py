"""
Tests para el Parser Agent (Lark → AST custom)
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.modules.parser.service import get_parser_agent
from app.models.ast_nodes import (
    Program, Function, For, While, If, Assign,
    Var, Literal, BinOp, Compare
)


def test_simple_procedure():
    """Test: Procedimiento simple con asignación"""
    code = """
    procedimiento suma(a, b)
    begin
        resultado 🡨 a + b
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    assert isinstance(ast, Program)
    assert len(ast.functions) == 1
    
    func = ast.functions[0]
    assert func.name == "suma"
    assert len(func.params) == 2
    assert func.params[0].name == "a"
    assert func.params[1].name == "b"
    
    # Verificar body
    assert len(func.body.statements) == 1
    stmt = func.body.statements[0]
    assert isinstance(stmt, Assign)
    assert isinstance(stmt.target, Var)
    assert stmt.target.name == "resultado"
    
    # Verificar expresión a + b
    assert isinstance(stmt.value, BinOp)
    assert stmt.value.op == "+"
    
    print("✓ test_simple_procedure PASSED")


def test_for_loop():
    """Test: Bucle for con array"""
    code = """
    procedimiento buscar(arr, n)
    begin
        for i 🡨 1 to n do
        begin
            if arr[i] = 0 then
            begin
                return i
            end
        end
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    func = ast.functions[0]
    assert func.name == "buscar"
    
    # Verificar bucle for
    for_stmt = func.body.statements[0]
    assert isinstance(for_stmt, For)
    assert for_stmt.var == "i"
    assert isinstance(for_stmt.start, Literal)
    assert for_stmt.start.value == 1
    assert isinstance(for_stmt.end, Var)
    assert for_stmt.end.name == "n"
    
    # Verificar if dentro del for
    if_stmt = for_stmt.body.statements[0]
    assert isinstance(if_stmt, If)
    
    # Verificar condición arr[i] = 0
    assert isinstance(if_stmt.cond, Compare)
    assert if_stmt.cond.op == "=="
    
    print("✓ test_for_loop PASSED")


def test_bubble_sort():
    """Test: Algoritmo bubble sort completo"""
    code = """
    procedimiento ordenamientoBurbuja(A, n)
    begin
        for i 🡨 1 to n - 1 do
        begin
            for j 🡨 1 to n - i do
            begin
                if A[j] > A[j + 1] then
                begin
                    temp 🡨 A[j]
                    A[j] 🡨 A[j + 1]
                    A[j + 1] 🡨 temp
                end
            end
        end
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    assert isinstance(ast, Program)
    assert len(ast.functions) == 1
    
    func = ast.functions[0]
    assert func.name == "ordenamientoBurbuja"
    assert len(func.params) == 2
    
    # Verificar estructura: for -> for -> if -> 3 assigns
    outer_for = func.body.statements[0]
    assert isinstance(outer_for, For)
    assert outer_for.var == "i"
    
    inner_for = outer_for.body.statements[0]
    assert isinstance(inner_for, For)
    assert inner_for.var == "j"
    
    if_stmt = inner_for.body.statements[0]
    assert isinstance(if_stmt, If)
    
    # Verificar las 3 asignaciones dentro del if
    then_block = if_stmt.then_block
    assert len(then_block.statements) == 3
    assert all(isinstance(s, Assign) for s in then_block.statements)
    
    print("✓ test_bubble_sort PASSED")


def test_while_loop():
    """Test: Bucle while"""
    code = """
    procedimiento busqueda(arr, n, target)
    begin
        i 🡨 1
        while i ≤ n and arr[i] ≠ target do
        begin
            i 🡨 i + 1
        end
        return i
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    func = ast.functions[0]
    
    # Primera sentencia: asignación i 🡨 1
    assert isinstance(func.body.statements[0], Assign)
    
    # Segunda sentencia: while
    while_stmt = func.body.statements[1]
    assert isinstance(while_stmt, While)
    
    # Condición: i <= n AND arr[i] != target
    cond = while_stmt.cond
    assert isinstance(cond, BinOp)
    assert cond.op == "and"
    
    # Body del while: i 🡨 i + 1
    assert len(while_stmt.body.statements) == 1
    assign = while_stmt.body.statements[0]
    assert isinstance(assign, Assign)
    assert assign.target.name == "i"
    
    print("✓ test_while_loop PASSED")


def test_nested_conditions():
    """Test: Condicionales anidados"""
    code = """
    procedimiento clasificar(x)
    begin
        if x > 0 then
        begin
            if x > 10 then
            begin
                resultado 🡨 2
            end
            else
            begin
                resultado 🡨 1
            end
        end
        else
        begin
            resultado 🡨 0
        end
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    func = ast.functions[0]
    outer_if = func.body.statements[0]
    
    assert isinstance(outer_if, If)
    assert outer_if.else_block is not None
    
    # Verificar if anidado en then_block
    inner_if = outer_if.then_block.statements[0]
    assert isinstance(inner_if, If)
    assert inner_if.else_block is not None
    
    print("✓ test_nested_conditions PASSED")


def test_ast_serialization():
    """Test: Serialización del AST a diccionario"""
    code = """
    procedimiento factorial(n)
    begin
        if n ≤ 1 then
        begin
            return 1
        end
        else
        begin
            return n * factorial(n - 1)
        end
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    # Serializar a diccionario
    ast_dict = ast.to_dict()
    
    assert ast_dict["type"] == "Program"
    assert "functions" in ast_dict
    assert len(ast_dict["functions"]) == 1
    
    func_dict = ast_dict["functions"][0]
    assert func_dict["type"] == "Function"
    assert func_dict["name"] == "factorial"
    assert len(func_dict["params"]) == 1
    assert func_dict["params"][0]["name"] == "n"
    
    # Verificar que body es serializable
    assert "body" in func_dict
    assert func_dict["body"]["type"] == "Block"
    
    print("✓ test_ast_serialization PASSED")


def test_comparison_operators():
    """Test: Diferentes operadores de comparación"""
    code = """
    procedimiento comparar(a, b)
    begin
        r1 🡨 a = b
        r2 🡨 a ≠ b
        r3 🡨 a < b
        r4 🡨 a ≤ b
        r5 🡨 a > b
        r6 🡨 a ≥ b
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    func = ast.functions[0]
    statements = func.body.statements
    
    # Verificar operadores normalizados
    assert statements[0].value.op == "=="
    assert statements[1].value.op == "!="
    assert statements[2].value.op == "<"
    assert statements[3].value.op == "<="
    assert statements[4].value.op == ">"
    assert statements[5].value.op == ">="
    
    print("✓ test_comparison_operators PASSED")


def test_langgraph_interface():
    """Test: Interfaz compatible con LangGraph"""
    code = """
    procedimiento simple()
    begin
        x 🡨 1
    end
    """
    
    parser = get_parser_agent()
    
    # Llamar usando interfaz LangGraph
    result = parser({"pseudocode": code})
    
    assert result["success"] == True
    assert result["ast"] is not None
    assert result["error"] is None
    assert isinstance(result["ast"], Program)
    
    print("✓ test_langgraph_interface PASSED")


def test_error_handling():
    """Test: Manejo de errores de sintaxis"""
    code = """
    procedimiento invalido(
        x 🡨 1
    """
    
    parser = get_parser_agent()
    
    # Llamar usando interfaz LangGraph
    result = parser({"pseudocode": code})
    
    assert result["success"] == False
    assert result["ast"] is None
    assert result["error"] is not None
    assert len(result["error"]) > 0
    
    print("✓ test_error_handling PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTS DEL PARSER AGENT (Lark → AST)")
    print("=" * 60)
    
    tests = [
        test_simple_procedure,
        test_for_loop,
        test_bubble_sort,
        test_while_loop,
        test_nested_conditions,
        test_ast_serialization,
        test_comparison_operators,
        test_langgraph_interface,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} FAILED: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    print("=" * 60)
    print(f"RESUMEN: {passed} passed, {failed} failed")
    print("=" * 60)
    
    sys.exit(0 if failed == 0 else 1)
