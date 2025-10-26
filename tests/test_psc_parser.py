"""
Tests para el parser de pseudocódigo (psc_parser.py).
"""
import pytest
from app.core.psc_parser import PseudocodeParser
from app.models.ast_nodes import (
    Program, Function, Block, For, While, If, Assign, Return,
    Var, Literal, BinOp, Compare, ArrayAccess, Call
)


def test_sum_array_with_for():
    """Test básico: suma de array con for loop"""
    code = """
    procedimiento suma_array(arr, n)
    begin
        suma 🡨 0
        for i 🡨 0 to n - 1 do
        begin
            suma 🡨 suma + arr[i]
        end
        return suma
    end
    """
    
    parser = PseudocodeParser()
    program = parser.build(code)
    
    assert isinstance(program, Program)
    assert len(program.functions) == 1
    
    func = program.functions[0]
    assert func.name == "suma_array"
    assert len(func.params) == 2
    assert func.params[0].name == "arr"
    assert func.params[1].name == "n"
    
    # Verificar body
    assert isinstance(func.body, Block)
    stmts = func.body.statements
    assert len(stmts) == 3  # suma=0, for, return
    
    # Primera: suma 🡨 0
    assert isinstance(stmts[0], Assign)
    assert isinstance(stmts[0].target, Var)
    assert stmts[0].target.name == "suma"
    
    # Segunda: for loop
    assert isinstance(stmts[1], For)
    assert stmts[1].var == "i"
    
    # Tercera: return
    assert isinstance(stmts[2], Return)


def test_factorial_with_if():
    """Test: factorial con if-else"""
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
    
    parser = PseudocodeParser()
    program = parser.build(code)
    
    func = program.functions[0]
    assert func.name == "factorial"
    
    # Body tiene 1 statement: if
    stmts = func.body.statements
    assert len(stmts) == 1
    assert isinstance(stmts[0], If)
    
    if_stmt = stmts[0]
    
    # Verificar condición: n ≤ 1
    assert isinstance(if_stmt.cond, Compare)
    assert if_stmt.cond.op == "<="
    
    # Verificar then block: return 1
    assert isinstance(if_stmt.then_block, Block)
    assert len(if_stmt.then_block.statements) == 1
    assert isinstance(if_stmt.then_block.statements[0], Return)
    
    # Verificar else block: return n * factorial(n-1)
    assert if_stmt.else_block is not None
    assert isinstance(if_stmt.else_block, Block)
    assert len(if_stmt.else_block.statements) == 1
    assert isinstance(if_stmt.else_block.statements[0], Return)


def test_binary_search_with_while():
    """Test: búsqueda binaria con while"""
    code = """
    procedimiento buscar(arr, objetivo, n)
    begin
        izq 🡨 0
        der 🡨 n - 1
        while izq ≤ der do
        begin
            medio 🡨 (izq + der) / 2
            if arr[medio] = objetivo then
            begin
                return medio
            end
            if arr[medio] < objetivo then
            begin
                izq 🡨 medio + 1
            end
            else
            begin
                der 🡨 medio - 1
            end
        end
        return -1
    end
    """
    
    parser = PseudocodeParser()
    program = parser.build(code)
    
    func = program.functions[0]
    assert func.name == "buscar"
    assert len(func.params) == 3
    
    stmts = func.body.statements
    # izq=0, der=n-1, while, return
    assert len(stmts) == 4
    
    # Verificar while loop
    assert isinstance(stmts[2], While)
    while_stmt = stmts[2]
    
    # Condición: izq ≤ der
    assert isinstance(while_stmt.cond, Compare)
    assert while_stmt.cond.op == "<="
    
    # Body del while tiene: medio=..., if arr[medio]=objetivo, if arr[medio]<objetivo
    assert isinstance(while_stmt.body, Block)
    assert len(while_stmt.body.statements) >= 2


def test_nested_loops():
    """Test: loops anidados (matriz)"""
    code = """
    procedimiento suma_matriz(matriz, filas, cols)
    begin
        suma 🡨 0
        for i 🡨 0 to filas - 1 do
        begin
            for j 🡨 0 to cols - 1 do
            begin
                suma 🡨 suma + matriz[i][j]
            end
        end
        return suma
    end
    """
    
    parser = PseudocodeParser()
    program = parser.build(code)
    
    func = program.functions[0]
    stmts = func.body.statements
    
    # suma=0, for i, return
    assert len(stmts) == 3
    
    # For externo
    outer_for = stmts[1]
    assert isinstance(outer_for, For)
    assert outer_for.var == "i"
    
    # For interno (primer statement del for externo)
    inner_for = outer_for.body.statements[0]
    assert isinstance(inner_for, For)
    assert inner_for.var == "j"


def test_call_statement():
    """Test: CALL statement"""
    code = """
    procedimiento main()
    begin
        arr 🡨 [1, 2, 3]
        CALL imprimir(arr)
        resultado 🡨 suma(arr, 3)
        return resultado
    end
    """
    
    parser = PseudocodeParser()
    program = parser.build(code)
    
    func = program.functions[0]
    stmts = func.body.statements
    
    # arr=..., CALL imprimir, resultado=suma(...), return
    assert len(stmts) >= 2
    
    # Buscar el CALL statement
    # TODO: Verificar que hay un ExprStmt con Call


def test_comparison_operators():
    """Test: operadores de comparación (=, ≠, <, >, ≤, ≥)"""
    code = """
    procedimiento comparar(a, b)
    begin
        if a = b then
            return 0
        if a ≠ b then
            return 1
        if a < b then
            return -1
        if a > b then
            return 2
        if a ≤ b then
            return -2
        if a ≥ b then
            return 3
        return 99
    end
    """
    
    parser = PseudocodeParser()
    program = parser.build(code)
    
    func = program.functions[0]
    stmts = func.body.statements
    
    # Verificar que hay múltiples if statements
    if_count = sum(1 for s in stmts if isinstance(s, If))
    assert if_count >= 4  # Al menos 4 comparaciones


def test_repeat_until():
    """Test: repeat-until loop (convertido a while)"""
    code = """
    procedimiento contar()
    begin
        i 🡨 0
        repeat
        begin
            i 🡨 i + 1
        end
        until i ≥ 10
        return i
    end
    """
    
    parser = PseudocodeParser()
    program = parser.build(code)
    
    func = program.functions[0]
    stmts = func.body.statements
    
    # i=0, while (repeat convertido), return
    assert len(stmts) == 3
    
    # Verificar que el repeat se convirtió a while
    assert isinstance(stmts[1], While)
    
    # La condición debe estar negada (not (i >= 10))
    # o sea: while not (i >= 10)
    while_stmt = stmts[1]
    # TODO: verificar que la condición está negada


def test_invalid_pseudocode():
    """Test: pseudocódigo inválido debe fallar"""
    code = """
    procedimiento invalido()
    begin
        esto no es sintaxis válida !!!
    end
    """
    
    parser = PseudocodeParser()
    
    with pytest.raises(Exception) as exc_info:
        parser.build(code)
    
    assert "Error parsing pseudocode" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
