#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test para verificar que se generen ambos conjuntos de pasos del solver
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

# Código simple
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
end
"""

print("=" * 80)
print("TEST: Dos metodos de resolucion (por bloques y por lineas)")
print("=" * 80)
print()

# Parsear
parser = get_parser_agent()
ast = parser.parse(codigo)

# Analizar
analyzer = CostAnalyzerAgent()
costs = analyzer.analyze(ast, codigo)

print(f"Total nodos: {len(costs.per_node)}")
print(f"Total lineas: {len(costs.per_line)}")
print()

# Resolver con ambos métodos
solver = get_series_solver()
solution = solver.solve(costs.total, show_steps=True, per_line_costs=costs.per_line)

print("=" * 80)
print("METODO 1: Por bloques")
print("=" * 80)
print(f"Total pasos: {len(solution.steps)}")
print()
print("Primeros 5 pasos:")
for step in solution.steps[:5]:
    print(f"  Paso {step.step_number}: {step.description}")
print()

print("=" * 80)
print("METODO 2: Por lineas")
print("=" * 80)
print(f"Total pasos: {len(solution.steps_by_line)}")
print()
if solution.steps_by_line:
    # Filtrar solo pasos del peor caso
    worst_steps = [s for s in solution.steps_by_line if s.case == "worst"]
    print(f"Mostrando primeros 15 pasos del peor caso (de {len(worst_steps)} totales):")
    print()
    for step in worst_steps[:15]:
        desc = step.description[:70] if len(step.description) > 70 else step.description
        expr = step.expression[:80] if len(step.expression) > 80 else step.expression
        print(f"  [Paso {step.step_number}] {desc}")
        print(f"    {expr}")
        print()
else:
    print("  (No se generaron pasos por lineas)")

print("=" * 80)
print("RESULTADO FINAL (debe ser igual en ambos metodos)")
print("=" * 80)
print(f"Best:  {solution.exact.best}")
print(f"Avg:   {solution.exact.avg}")
print(f"Worst: {solution.exact.worst}")
print(f"Big-O: {solution.big_o.worst}")
print()

if len(solution.steps_by_line) > 0:
    print("[OK] Se generaron ambos conjuntos de pasos!")
else:
    print("[ERROR] Falta el metodo por lineas")
