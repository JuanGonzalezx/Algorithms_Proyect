"""
Ejemplo de uso del Cost Analyzer Agent
Demuestra el flujo completo: pseudocódigo → validación → AST → costos
"""
from app.modules.syntax_validator.agent import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import get_cost_analyzer
from app.shared.models import PseudocodeIn
import json


def ejemplo_flujo_completo():
    """Ejemplo 1: Flujo completo de análisis"""
    print("=" * 60)
    print("EJEMPLO 1: Flujo completo (Validación → Parse → Costos)")
    print("=" * 60)
    
    code = """
    procedimiento suma(a, b)
    begin
        resultado 🡨 a + b
        return resultado
    end
    """
    
    # Paso 1: Validar sintaxis
    validator = get_syntax_validator()
    validation = validator.validate(PseudocodeIn(text=code))
    
    print(f"✓ Validación: {'OK' if validation.era_algoritmo_valido else 'ERROR'}")
    
    # Paso 2: Parsear a AST
    parser = get_parser_agent()
    ast = parser.parse(validation.codigo_corregido)
    
    print(f"✓ Parsing: {len(ast.functions)} función(es)")
    
    # Paso 3: Analizar costos
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    
    print(f"✓ Análisis: {len(costs.per_node)} nodos analizados")
    print(f"\nCosto total:")
    print(f"  - Mejor caso: {costs.total.best}")
    print(f"  - Caso promedio: {costs.total.avg}")
    print(f"  - Peor caso: {costs.total.worst}")
    print()


def ejemplo_bubble_sort():
    """Ejemplo 2: Bubble Sort - Análisis completo"""
    print("=" * 60)
    print("EJEMPLO 2: Bubble Sort")
    print("=" * 60)
    
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
    
    # Procesar
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    
    print(f"Algoritmo: Bubble Sort")
    print(f"Nodos analizados: {len(costs.per_node)}")
    print()
    
    # Mostrar costos por nodo
    print("Costos por nodo:")
    for node in costs.per_node:
        print(f"  [{node.node_id}] {node.node_type}:")
        print(f"    Peor caso: {node.cost.worst}")
    
    print()
    print(f"Costo total (peor caso):")
    print(f"  {costs.total.worst}")
    print()


def ejemplo_busqueda_lineal():
    """Ejemplo 3: Búsqueda lineal con while"""
    print("=" * 60)
    print("EJEMPLO 3: Búsqueda Lineal")
    print("=" * 60)
    
    code = """
    procedimiento busqueda(arr, n, x)
    begin
        i 🡨 1
        encontrado 🡨 0
        while i ≤ n and encontrado = 0 do
        begin
            if arr[i] = x then
            begin
                encontrado 🡨 1
            end
            i 🡨 i + 1
        end
        return encontrado
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    
    print(f"Algoritmo: Búsqueda Lineal")
    print()
    print(f"Costo total:")
    print(f"  - Mejor caso: {costs.total.best}")
    print(f"    (elemento en primera posición)")
    print(f"  - Peor caso: {costs.total.worst}")
    print(f"    (elemento no encontrado o en última posición)")
    print()


def ejemplo_comparacion_algoritmos():
    """Ejemplo 4: Comparación de algoritmos"""
    print("=" * 60)
    print("EJEMPLO 4: Comparación - Suma iterativa vs recursiva")
    print("=" * 60)
    
    # Suma iterativa
    code_iterativo = """
    procedimiento sumaIterativa(n)
    begin
        suma 🡨 0
        for i 🡨 1 to n do
        begin
            suma 🡨 suma + i
        end
        return suma
    end
    """
    
    # Suma usando fórmula
    code_formula = """
    procedimiento sumaFormula(n)
    begin
        resultado 🡨 n * (n + 1) / 2
        return resultado
    end
    """
    
    parser = get_parser_agent()
    analyzer = get_cost_analyzer()
    
    # Analizar iterativo
    ast1 = parser.parse(code_iterativo)
    costs1 = analyzer.analyze(ast1)
    
    # Analizar fórmula
    ast2 = parser.parse(code_formula)
    costs2 = analyzer.analyze(ast2)
    
    print("Suma Iterativa:")
    print(f"  Costo: {costs1.total.worst}")
    print()
    print("Suma con Fórmula:")
    print(f"  Costo: {costs2.total.worst}")
    print()
    print("Conclusión: La fórmula es O(1), la iteración es O(n)")
    print()


def ejemplo_json_output():
    """Ejemplo 5: Salida en formato JSON"""
    print("=" * 60)
    print("EJEMPLO 5: Exportar a JSON")
    print("=" * 60)
    
    code = """
    procedimiento test(n)
    begin
        x 🡨 0
        for i 🡨 1 to n do
        begin
            x 🡨 x + 1
        end
        return x
    end
    """
    
    parser = get_parser_agent()
    ast = parser.parse(code)
    
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    
    # Convertir a JSON
    costs_json = json.dumps(costs.model_dump(), indent=2, ensure_ascii=False)
    
    print("Resultado en JSON:")
    print(costs_json)
    print()


def ejemplo_langgraph():
    """Ejemplo 6: Uso en pipeline LangGraph"""
    print("=" * 60)
    print("EJEMPLO 6: Pipeline LangGraph")
    print("=" * 60)
    
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
    
    # Simular pipeline LangGraph
    print("Pipeline: Validación → Parsing → Análisis")
    
    # Paso 1
    validator = get_syntax_validator()
    validation_result = validator({"text": code, "language_hint": "es"})
    print(f"  1. Validación: {'✓' if validation_result['era_algoritmo_valido'] else '✗'}")
    
    # Paso 2
    parser = get_parser_agent()
    parse_result = parser({"pseudocode": validation_result["codigo_corregido"]})
    print(f"  2. Parsing: {'✓' if parse_result['success'] else '✗'}")
    
    # Paso 3
    analyzer = get_cost_analyzer()
    analysis_result = analyzer({"ast": parse_result["ast"]})
    print(f"  3. Análisis: {'✓' if analysis_result['success'] else '✗'}")
    
    if analysis_result["success"]:
        costs = analysis_result["costs"]
        print(f"\nCosto total (peor caso): {costs.total.worst}")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "COST ANALYZER - EJEMPLOS" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    ejemplos = [
        ejemplo_flujo_completo,
        ejemplo_bubble_sort,
        ejemplo_busqueda_lineal,
        ejemplo_comparacion_algoritmos,
        ejemplo_json_output,
        ejemplo_langgraph
    ]
    
    for ejemplo in ejemplos:
        try:
            ejemplo()
        except Exception as e:
            print(f"✗ Error en {ejemplo.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("=" * 60)
    print("FIN DE LOS EJEMPLOS")
    print("=" * 60)
