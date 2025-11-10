#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test para verificar que aparezcan TODAS las líneas del Bubble Sort
"""

from app.modules.syntax_validator.agent import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import CostAnalyzerAgent
from app.shared.models import PseudocodeIn

# Código normalizado del endpoint
codigo = """bubble_sort(A)
begin
  ► A es un arreglo de elementos comparables
  ► n es el tamaño del arreglo A
  local n, i, j, temp

  n 🡨 length(A)
  for i 🡨 1 to n-1 do
  begin
    for j 🡨 1 to n-i do
    begin
      if (A[j] > A[j+1]) then
      begin
        ► Intercambiar A[j] y A[j+1]
        temp 🡨 A[j]
        A[j] 🡨 A[j+1]
        A[j+1] 🡨 temp
      end
    end
  end
end
"""

print("=" * 80)
print("TEST: Todas las líneas del Bubble Sort")
print("=" * 80)
print()

# Parsear
parser = get_parser_agent()
ast = parser.parse(codigo)

# Analizar
analyzer = CostAnalyzerAgent()
costs = analyzer.analyze(ast, codigo)

print(f"Total lineas con costos: {len(costs.per_line)}")
print()

# Mostrar todas las líneas
for lc in costs.per_line:
    print(f"Linea {lc.line_number:2d}: {lc.code.strip()}")
    print(f"  Operaciones: {', '.join(lc.operations)}")
    print(f"  Costo (worst): {lc.cost.worst}")
    print()

print("=" * 80)
print("Líneas esperadas:")
print("  7: n ← length(A)")
print("  8: for i ← 1 to n-1 do")
print(" 10: for j ← 1 to n-i do")
print(" 12: if (A[j] > A[j+1]) then")
print(" 15: temp ← A[j]")
print(" 16: A[j] ← A[j+1]")
print(" 17: A[j+1] ← temp")
print("=" * 80)
