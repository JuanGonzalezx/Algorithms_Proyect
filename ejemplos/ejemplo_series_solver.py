"""
Ejemplos de uso del Series Solver.

Demuestra cómo usar el solver para:
1. Resolver sumatorias simples
2. Analizar algoritmos completos
3. Comparar complejidades
4. Exportar a JSON
"""
from app.modules.syntax_validator.agent import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import get_cost_analyzer
from app.modules.solver.solver import get_series_solver
from app.shared.models import PseudocodeIn, CostExpr
import json


def print_separator(title: str):
    """Imprime un separador visual."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_solution(solution):
    """Imprime una solución de forma legible."""
    print("\n📊 EXPRESIONES EXACTAS (sumatorias resueltas):")
    print(f"  🟢 Mejor caso:    {solution.exact.best}")
    print(f"  🟡 Caso promedio: {solution.exact.avg}")
    print(f"  🔴 Peor caso:     {solution.exact.worst}")
    
    print("\n📈 BIG-O (solo término dominante):")
    print(f"  🟢 Mejor caso:    {solution.big_o.best}")
    print(f"  🟡 Caso promedio: {solution.big_o.avg}")
    print(f"  🔴 Peor caso:     {solution.big_o.worst}")
    
    print("\n🎯 COTAS ASINTÓTICAS:")
    print(f"  Ω (omega - cota inferior): {solution.bounds.omega}")
    print(f"  Θ (theta - cota ajustada): {solution.bounds.theta}")
    print(f"  O (big-o - cota superior): {solution.bounds.big_o}")


# ============================================================================
# EJEMPLO 1: Uso directo del solver
# ============================================================================

def ejemplo_uso_directo():
    """Ejemplo: Usar el solver directamente con CostExpr."""
    print_separator("EJEMPLO 1: Uso Directo del Solver")
    
    solver = get_series_solver()
    
    # Caso 1: Suma simple
    print("\n🔹 Caso 1: Sum(1, (k, 1, n)) - Iteración lineal")
    cost = CostExpr(
        best="Sum(1, (k, 1, n))",
        avg="Sum(1, (k, 1, n))",
        worst="Sum(1, (k, 1, n))"
    )
    solution = solver.solve(cost)
    print_solution(solution)
    
    # Caso 2: Suma cuadrática
    print("\n\n🔹 Caso 2: Sum(Sum(1, (j, 1, n)), (i, 1, n)) - Bucle anidado")
    cost = CostExpr(
        best="Sum(Sum(1, (j, 1, n)), (i, 1, n))",
        avg="Sum(Sum(1, (j, 1, n)), (i, 1, n))",
        worst="Sum(Sum(1, (j, 1, n)), (i, 1, n))"
    )
    solution = solver.solve(cost)
    print_solution(solution)


# ============================================================================
# EJEMPLO 2: Pipeline completo - Bubble Sort
# ============================================================================

def ejemplo_bubble_sort():
    """Ejemplo: Análisis completo de Bubble Sort."""
    print_separator("EJEMPLO 2: Pipeline Completo - Bubble Sort")
    
    codigo = """
    procedimiento burbuja(A, n)
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
    
    print(f"\nCódigo:\n{codigo}")
    
    # Pipeline completo
    print("\n🔄 Ejecutando pipeline...")
    
    validator = get_syntax_validator()
    validation = validator.validate(PseudocodeIn(text=codigo))
    print("  ✓ Sintaxis validada")
    
    parser = get_parser_agent()
    ast = parser.parse(validation.codigo_corregido)
    print("  ✓ AST generado")
    
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    print(f"  ✓ Costos analizados ({len(costs.per_node)} nodos)")
    
    solver = get_series_solver()
    solution = solver.solve(costs.total)
    print("  ✓ Sumatorias resueltas")
    
    print_solution(solution)


# ============================================================================
# EJEMPLO 3: Búsqueda Lineal
# ============================================================================

def ejemplo_busqueda_lineal():
    """Ejemplo: Análisis de búsqueda lineal con mejor/peor caso."""
    print_separator("EJEMPLO 3: Búsqueda Lineal - Mejor vs Peor Caso")
    
    codigo = """
    procedimiento buscar(arr, n, x)
    begin
        i 🡨 1
        while i ≤ n do
        begin
            if arr[i] = x then
            begin
                return i
            end
            i 🡨 i + 1
        end
        return 0
    end
    """
    
    print(f"\nCódigo:\n{codigo}")
    
    # Pipeline completo
    validator = get_syntax_validator()
    validation = validator.validate(PseudocodeIn(text=codigo))
    
    parser = get_parser_agent()
    ast = parser.parse(validation.codigo_corregido)
    
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    
    solver = get_series_solver()
    solution = solver.solve(costs.total)
    
    print_solution(solution)
    
    print("\n💡 INTERPRETACIÓN:")
    print("  • Mejor caso: Elemento encontrado en primera posición → O(1)")
    print("  • Peor caso: Elemento no está o está al final → O(n)")


# ============================================================================
# EJEMPLO 4: Comparación de Algoritmos
# ============================================================================

def ejemplo_comparacion():
    """Ejemplo: Comparar complejidades de diferentes algoritmos."""
    print_separator("EJEMPLO 4: Comparación de Algoritmos")
    
    algoritmos = {
        "Constante": CostExpr(best="1", avg="1", worst="1"),
        "Lineal": CostExpr(
            best="Sum(1, (k, 1, n))",
            avg="Sum(1, (k, 1, n))",
            worst="Sum(1, (k, 1, n))"
        ),
        "Cuadrático": CostExpr(
            best="Sum(Sum(1, (j, 1, n)), (i, 1, n))",
            avg="Sum(Sum(1, (j, 1, n)), (i, 1, n))",
            worst="Sum(Sum(1, (j, 1, n)), (i, 1, n))"
        ),
    }
    
    solver = get_series_solver()
    
    print("\n📊 Comparación de complejidades:\n")
    print(f"{'Algoritmo':<15} {'Expresión Exacta':<25} {'Big-O':<15} {'Theta':<15}")
    print("-" * 70)
    
    for nombre, cost in algoritmos.items():
        solution = solver.solve(cost)
        print(f"{nombre:<15} {solution.exact.worst:<25} {solution.big_o.worst:<15} {solution.bounds.theta:<15}")


# ============================================================================
# EJEMPLO 5: Exportar a JSON
# ============================================================================

def ejemplo_json():
    """Ejemplo: Exportar resultados a JSON."""
    print_separator("EJEMPLO 5: Exportar Resultados a JSON")
    
    solver = get_series_solver()
    
    cost = CostExpr(
        best="1",
        avg="Sum(1, (k, 1, n))",
        worst="Sum(Sum(1, (j, 1, n)), (i, 1, n))"
    )
    
    solution = solver.solve(cost)
    
    # Serializar a JSON
    json_data = solution.model_dump()
    json_str = json.dumps(json_data, indent=2)
    
    print("\n📄 JSON Output:")
    print(json_str)
    
    print("\n✅ El resultado se puede:")
    print("  • Guardar en archivo")
    print("  • Enviar por API")
    print("  • Procesar por otros sistemas")


# ============================================================================
# EJEMPLO 6: Interfaz LangGraph
# ============================================================================

def ejemplo_langgraph():
    """Ejemplo: Usar interfaz LangGraph."""
    print_separator("EJEMPLO 6: Interfaz LangGraph")
    
    solver = get_series_solver()
    
    # Simular estado de LangGraph
    state = {
        "costs": CostExpr(
            best="1",
            avg="Sum(1, (k, 1, n))",
            worst="Sum(1, (k, 1, n))"
        )
    }
    
    print("\n📥 Estado de entrada:")
    print(f"  costs.worst = {state['costs'].worst}")
    
    # Ejecutar solver
    result = solver(state)
    
    print("\n📤 Estado de salida:")
    print(f"  success: {result['success']}")
    print(f"  error: {result['error']}")
    print(f"  solution.big_o.worst: {result['solution'].big_o.worst}")
    print(f"  solution.bounds.theta: {result['solution'].bounds.theta}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 18 + "EJEMPLOS: SERIES SOLVER" + " " * 27 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Ejecutar ejemplos
    ejemplo_uso_directo()
    input("\n\nPresiona Enter para continuar...")
    
    ejemplo_bubble_sort()
    input("\n\nPresiona Enter para continuar...")
    
    ejemplo_busqueda_lineal()
    input("\n\nPresiona Enter para continuar...")
    
    ejemplo_comparacion()
    input("\n\nPresiona Enter para continuar...")
    
    ejemplo_json()
    input("\n\nPresiona Enter para continuar...")
    
    ejemplo_langgraph()
    
    print("\n\n" + "=" * 70)
    print("EJEMPLOS COMPLETADOS")
    print("=" * 70)
    print("\n✅ Series Solver está funcionando correctamente!")
    print("🎯 Usa POST /api/v1/solve para el pipeline completo en Swagger\n")
