"""Debug simple: verificar qué recibe el solver"""
from app.modules.solver.solver import get_series_solver
from app.shared.models import CostExpr

solver = get_series_solver()

# La expresión que genera el cost_analyzer
cost = CostExpr(
    best="0",
    avg="Sum(Sum((1 + 1 + 1 + 0)/2, (k, 1, (n - i))), (j, 1, (n - 1)))",
    worst="Sum(Sum(max(1 + 1 + 1, 0), (k, 1, (n - i))), (j, 1, (n - 1)))"
)

print("Entrada:")
print(f"  worst = {cost.worst}")

result = solver.solve(cost)

print("\nSalida:")
print(f"  exact.worst = {result.exact.worst}")
print(f"  big_o.worst = {result.big_o.worst}")

import sympy as sp
print(f"\nVariables en exact.worst: {sp.sympify(result.exact.worst).free_symbols}")
