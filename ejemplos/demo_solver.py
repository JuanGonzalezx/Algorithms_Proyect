"""
Demo rápido: Pipeline completo con Bubble Sort
"""
from app.modules.syntax_validator.agent import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import get_cost_analyzer
from app.modules.solver.solver import get_series_solver
from app.shared.models import PseudocodeIn

print("\n" + "=" * 70)
print("DEMO RÁPIDO: Pipeline de 4 Agentes - Bubble Sort")
print("=" * 70)

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

# Pipeline
print("\n🔄 Ejecutando pipeline de 4 agentes...\n")

# 1. Validar sintaxis
validator = get_syntax_validator()
validation = validator.validate(PseudocodeIn(text=codigo))
print(f"✓ [1/4] Sintaxis validada (errores: {len(validation.errores)})")

# 2. Parsear AST
parser = get_parser_agent()
ast = parser.parse(validation.codigo_corregido)
print(f"✓ [2/4] AST generado (funciones: {len(ast.functions)})")

# 3. Analizar costos
analyzer = get_cost_analyzer()
costs = analyzer.analyze(ast)
print(f"✓ [3/4] Costos analizados (nodos: {len(costs.per_node)})")
print(f"    Peor caso (sumatorias): {costs.total.worst}")

# 4. Resolver sumatorias
solver = get_series_solver()
solution = solver.solve(costs.total)
print(f"✓ [4/4] Sumatorias resueltas")

# Resultados
print("\n" + "─" * 70)
print("📊 RESULTADOS DEL ANÁLISIS")
print("─" * 70)

print(f"\n🔢 Expresión exacta (peor caso):")
print(f"    {solution.exact.worst}")

print(f"\n📈 Big-O (término dominante):")
print(f"    Mejor caso:    {solution.big_o.best}")
print(f"    Caso promedio: {solution.big_o.avg}")
print(f"    Peor caso:     {solution.big_o.worst}")

print(f"\n🎯 Cotas asintóticas:")
print(f"    Ω (omega): {solution.bounds.omega}")
print(f"    Θ (theta): {solution.bounds.theta}")
print(f"    O (big-o): {solution.bounds.big_o}")

print("\n" + "=" * 70)
print("✅ Análisis completado exitosamente!")
print("=" * 70)

print("\n💡 Interpretación:")
print("   Bubble Sort tiene complejidad cuadrática O(n²)")
print("   • Mejor caso: No intercambios necesarios")
print("   • Peor caso: Array en orden inverso, requiere todas las comparaciones")
print()
