"""
Test detallado de los pasos del método por líneas
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.modules.syntax_validator.agent import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import CostAnalyzerAgent
from app.modules.solver.solver import get_series_solver
from app.shared.models import PseudocodeIn

# Código de burbuja
codigo = """bubble_sort(A)
begin
    n 🡨 length(A)
    for i 🡨 1 to n-1 do
    begin
        for j 🡨 1 to n-i do
        begin
            if (A[j] > A[j+1]) then
            begin
                temp 🡨 A[j]
                A[j] 🡨 A[j+1]
                A[j+1] 🡨 temp
            end
        end
    end
end"""

print("=" * 80)
print("TEST DETALLADO: Pasos del Método Por Líneas")
print("=" * 80)

# Validar
validator = get_syntax_validator()
validation = validator.validate(PseudocodeIn(text=codigo))

# Parsear
parser = get_parser_agent()
ast = parser.parse(validation.codigo_corregido)

# Analizar costos
analyzer = CostAnalyzerAgent()
costs = analyzer.analyze(ast)

print(f"\nCostos generados:")
print(f"  - Nodos analizados: {len(costs.per_node)}")
print(f"  - Lineas con costo: {len(costs.per_line)}")

if costs.per_line:
    print(f"\nLineas:")
    for lc in costs.per_line:
        print(f"  L{lc.line_number}: {lc.operations} - worst={lc.cost.worst}")

# Resolver con ambos métodos
solver = get_series_solver()
solution = solver.solve(costs.total, show_steps=True, per_line_costs=costs.per_line)

print(f"\n✅ Total pasos método por bloques: {len(solution.steps)}")
print(f"✅ Total pasos método por líneas: {len(solution.steps_by_line)}\n")

# Mostrar TODOS los pasos del método por líneas (solo peor caso)
worst_steps = [s for s in solution.steps_by_line if s.case == "worst"]

print("=" * 80)
print(f"PASOS DEL MÉTODO POR LÍNEAS (PEOR CASO) - Total: {len(worst_steps)}")
print("=" * 80)

for step in worst_steps:
    print(f"\n[Paso {step.step_number}] {step.description}")
    # Limitar expresión a 100 caracteres para legibilidad
    expr = step.expression
    if len(expr) > 100:
        expr = expr[:97] + "..."
    print(f"  {expr}")

print("\n" + "=" * 80)
print("VERIFICACIÓN:")
print("=" * 80)

# Buscar pasos de resolución de sumatorias
sum_steps = [s for s in worst_steps if "sumatoria" in s.description.lower() and "resolver" in s.description.lower()]

if sum_steps:
    print(f"\n✅ Se encontraron {len(sum_steps)} pasos de resolución de sumatorias:")
    for step in sum_steps:
        print(f"  - Paso {step.step_number}: {step.description}")
else:
    print("\n❌ No se encontraron pasos de resolución de sumatorias")

# Verificar que se resuelven de adentro hacia afuera
if len(sum_steps) >= 2:
    first = sum_steps[0]
    second = sum_steps[1]
    
    print(f"\n📋 Orden de resolución:")
    print(f"  1° {first.description}")
    print(f"  2° {second.description}")
    
    if "interna" in first.description.lower() or "(j" in first.expression:
        print("  ✅ Correcto: Primero resuelve la sumatoria interna")
    else:
        print("  ⚠️ Verificar orden de resolución")

print("\n" + "=" * 80)
