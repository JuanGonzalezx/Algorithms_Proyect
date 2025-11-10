"""
Tests para el Cost Analyzer Agent (AST → Sumatorias)
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import get_cost_analyzer


def test_simple_assign():
    """Test: Asignación simple tiene costo 1"""
    code = """
    procedimiento test()
    begin
        x 🡨 1
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    
    # Verificar que hay costos
    assert len(costs.per_node) > 0
    
    # Buscar el nodo Assign
    assign_node = next((n for n in costs.per_node if n.node_type == "Assign"), None)
    assert assign_node is not None
    assert assign_node.cost.best == "1"
    assert assign_node.cost.avg == "1"
    assert assign_node.cost.worst == "1"
    
    print("✓ test_simple_assign PASSED")


def test_for_loop():
    """Test: Bucle for genera sumatoria"""
    code = """
    procedimiento test(n)
    begin
        for i 🡨 1 to n do
        begin
            x 🡨 1
        end
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    
    # Buscar el nodo For
    for_node = next((n for n in costs.per_node if n.node_type == "For"), None)
    assert for_node is not None
    
    # Debe contener "Sum"
    assert "Sum" in for_node.cost.best
    assert "Sum" in for_node.cost.avg
    assert "Sum" in for_node.cost.worst
    
    print(f"✓ test_for_loop PASSED")
    print(f"  Costo For: {for_node.cost.worst}")


def test_nested_for():
    """Test: Bucles for anidados generan sumatorias anidadas"""
    code = """
    procedimiento bubbleSort(A, n)
    begin
        for i 🡨 1 to n - 1 do
        begin
            for j 🡨 1 to n - i do
            begin
                temp 🡨 A[j]
            end
        end
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    
    # Buscar nodos For
    for_nodes = [n for n in costs.per_node if n.node_type == "For"]
    assert len(for_nodes) == 2  # Dos bucles for
    
    # El for externo debe tener sumatoria anidada
    outer_for = for_nodes[1]  # El último registrado es el externo
    assert "Sum" in outer_for.cost.worst
    
    # Verificar que hay doble sumatoria (Sum dentro de Sum)
    assert outer_for.cost.worst.count("Sum") >= 2
    
    print(f"✓ test_nested_for PASSED")
    print(f"  Costo For externo: {outer_for.cost.worst}")


def test_if_statement():
    """Test: Condicional if considera mejor y peor caso"""
    code = """
    procedimiento test(x)
    begin
        if x > 0 then
        begin
            a 🡨 1
            b 🡨 2
            c 🡨 3
        end
        else
        begin
            d 🡨 4
        end
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    
    # Buscar el nodo If
    if_node = next((n for n in costs.per_node if n.node_type == "If"), None)
    assert if_node is not None
    
    # El mejor caso debe ser menor o igual que el peor caso
    # En este caso: then=3, else=1
    # Mejor=min(3,1)=1, Peor=max(3,1)=3
    assert "min" in if_node.cost.best or if_node.cost.best == "1"
    assert "max" in if_node.cost.worst or if_node.cost.worst == "3"
    
    print(f"✓ test_if_statement PASSED")
    print(f"  Mejor caso: {if_node.cost.best}")
    print(f"  Peor caso: {if_node.cost.worst}")


def test_while_loop():
    """Test: Bucle while tiene diferente mejor y peor caso"""
    code = """
    procedimiento test(n)
    begin
        i 🡨 1
        while i < n do
        begin
            i 🡨 i + 1
        end
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    
    # Buscar el nodo While
    while_node = next((n for n in costs.per_node if n.node_type == "While"), None)
    assert while_node is not None
    
    # Mejor caso: 1 evaluación del guard (condición falsa inicialmente)
    assert while_node.cost.best == "1"
    
    # Peor caso: debe tener sumatoria
    assert "Sum" in while_node.cost.worst
    
    print(f"✓ test_while_loop PASSED")
    print(f"  Mejor caso: {while_node.cost.best}")
    print(f"  Peor caso: {while_node.cost.worst}")


def test_complete_program():
    """Test: Programa completo calcula costo total"""
    code = """
    procedimiento bubbleSort(A, n)
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
    
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    
    # Verificar que hay costo total
    assert costs.total is not None
    assert costs.total.best is not None
    assert costs.total.avg is not None
    assert costs.total.worst is not None
    
    # Debe contener sumatorias
    assert "Sum" in costs.total.worst
    
    # Verificar que hay nodos analizados
    assert len(costs.per_node) > 0
    
    print(f"✓ test_complete_program PASSED")
    print(f"  Nodos analizados: {len(costs.per_node)}")
    print(f"  Costo total (peor caso): {costs.total.worst}")


def test_serialization():
    """Test: Los costos son serializables a JSON"""
    code = """
    procedimiento test(n)
    begin
        for i 🡨 1 to n do
        begin
            x 🡨 1
        end
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    
    # Serializar a diccionario
    costs_dict = costs.dict()
    
    assert "per_node" in costs_dict
    assert "total" in costs_dict
    assert isinstance(costs_dict["per_node"], list)
    assert isinstance(costs_dict["total"], dict)
    
    # Verificar estructura de un nodo
    if costs_dict["per_node"]:
        node = costs_dict["per_node"][0]
        assert "node_id" in node
        assert "node_type" in node
        assert "cost" in node
        assert "best" in node["cost"]
        assert "avg" in node["cost"]
        assert "worst" in node["cost"]
    
    print("✓ test_serialization PASSED")


def test_langgraph_interface():
    """Test: Interfaz compatible con LangGraph"""
    code = """
    procedimiento test()
    begin
        x 🡨 1
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    analyzer = get_cost_analyzer()
    
    # Llamar usando interfaz LangGraph
    result = analyzer({"ast": ast})
    
    assert result["success"] == True
    assert result["costs"] is not None
    assert result["error"] is None
    
    print("✓ test_langgraph_interface PASSED")


def test_multiple_functions():
    """Test: Múltiples funciones se suman"""
    code = """
    procedimiento func1()
    begin
        x 🡨 1
    end
    
    procedimiento func2()
    begin
        y 🡨 2
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    
    # Buscar nodos Function
    func_nodes = [n for n in costs.per_node if n.node_type == "Function"]
    assert len(func_nodes) == 2
    
    # El costo total debe considerar ambas funciones
    assert "+" in costs.total.worst or costs.total.worst == "2"
    
    print("✓ test_multiple_functions PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTS DEL COST ANALYZER AGENT (AST → Sumatorias)")
    print("=" * 60)
    
    tests = [
        test_simple_assign,
        test_for_loop,
        test_nested_for,
        test_if_statement,
        test_while_loop,
        test_complete_program,
        test_serialization,
        test_langgraph_interface,
        test_multiple_functions
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
