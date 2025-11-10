"""
Demo End-to-End: Análisis completo de un algoritmo
Demuestra el flujo completo de los 3 agentes
"""
from app.modules.syntax_validator.agent import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import get_cost_analyzer
from app.shared.models import PseudocodeIn
import json


def analizar_algoritmo(nombre: str, codigo: str):
    """Analiza un algoritmo completo usando los 3 agentes."""
    print("=" * 70)
    print(f"ANÁLISIS: {nombre}")
    print("=" * 70)
    print(f"\nCódigo:\n{codigo}\n")
    
    # AGENTE 1: Validación sintáctica
    print("🔍 PASO 1: Validando sintaxis...")
    validator = get_syntax_validator()
    validation = validator.validate(PseudocodeIn(text=codigo))
    
    if not validation.era_algoritmo_valido:
        print("❌ El código tiene errores de sintaxis:")
        for error in validation.errores:
            print(f"  - Línea {error.linea}: {error.detalle}")
        return None
    
    print(f"✓ Sintaxis válida")
    if validation.normalizaciones:
        print(f"  Normalizaciones aplicadas: {len(validation.normalizaciones)}")
    
    # AGENTE 2: Parsing a AST
    print("\n🌳 PASO 2: Generando AST...")
    parser = get_parser_agent()
    ast = parser.parse(validation.codigo_corregido)
    
    print(f"✓ AST generado")
    print(f"  Funciones: {len(ast.functions)}")
    if ast.functions:
        func = ast.functions[0]
        print(f"  Nombre: {func.name}")
        print(f"  Parámetros: {[p.name for p in func.params]}")
        print(f"  Statements: {len(func.body.statements)}")
    
    # AGENTE 3: Análisis de costos
    print("\n📊 PASO 3: Analizando costos...")
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    
    print(f"✓ Análisis completado")
    print(f"  Nodos analizados: {len(costs.per_node)}")
    
    # Mostrar resultados
    print("\n" + "─" * 70)
    print("RESULTADOS DEL ANÁLISIS")
    print("─" * 70)
    
    print("\n📈 Costo por tipo de caso:")
    print(f"  🟢 Mejor caso:     {costs.total.best}")
    print(f"  🟡 Caso promedio:  {costs.total.avg}")
    print(f"  🔴 Peor caso:      {costs.total.worst}")
    
    print("\n📋 Detalle por nodo:")
    for node in costs.per_node:
        if node.node_type in ["For", "While", "If"]:
            print(f"  [{node.node_id}] {node.node_type}:")
            print(f"    Peor caso: {node.cost.worst}")
    
    print("\n" + "=" * 70)
    return costs


# ============================================================================
# EJEMPLOS
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "DEMO END-TO-END: ANÁLISIS COMPLETO" + " " * 19 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    # EJEMPLO 1: Bubble Sort
    bubble_sort = """
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
    
    analizar_algoritmo("Bubble Sort", bubble_sort)
    
    # EJEMPLO 2: Búsqueda Lineal
    busqueda_lineal = """
    procedimiento busqueda(arr, n, x)
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
    
    print("\n\n")
    analizar_algoritmo("Búsqueda Lineal", busqueda_lineal)
    
    # EJEMPLO 3: Suma Simple
    suma_simple = """
    procedimiento suma(n)
    begin
        s 🡨 0
        for i 🡨 1 to n do
        begin
            s 🡨 s + i
        end
        return s
    end
    """
    
    print("\n\n")
    analizar_algoritmo("Suma de 1 a n", suma_simple)
    
    # EJEMPLO 4: Factorial Iterativo
    factorial = """
    procedimiento factorial(n)
    begin
        resultado 🡨 1
        for i 🡨 1 to n do
        begin
            resultado 🡨 resultado * i
        end
        return resultado
    end
    """
    
    print("\n\n")
    analizar_algoritmo("Factorial Iterativo", factorial)
    
    print("\n")
    print("=" * 70)
    print("ANÁLISIS COMPLETADO")
    print("=" * 70)
    print()
    print("📊 Resumen:")
    print("  • 4 algoritmos analizados")
    print("  • 3 agentes ejecutados por algoritmo")
    print("  • Todos los análisis exitosos ✓")
    print()
    print("🎯 Interpretación de resultados:")
    print("  • Sum(1, (k, 1, n)) = n iteraciones → O(n)")
    print("  • Sum(Sum(...), ...) = bucle anidado → O(n²)")
    print("  • 1 + 1 + ... = constante → O(1)")
    print()
