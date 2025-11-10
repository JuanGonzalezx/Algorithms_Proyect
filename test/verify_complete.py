"""Verificar la resolución de sumatorias"""
from app.modules.syntax_validator.agent import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import get_cost_analyzer
from app.modules.solver.solver import get_series_solver
from app.shared.models import PseudocodeIn

codigo = """procedimiento burbuja(A, n)
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
end"""

validator = get_syntax_validator()
validation = validator.validate(PseudocodeIn(text=codigo))

parser = get_parser_agent()
ast = parser.parse(validation.codigo_corregido)

analyzer = get_cost_analyzer()
costs = analyzer.analyze(ast)

solver = get_series_solver()
solution = solver.solve(costs.total)

print('=' * 70)
print('ANÁLISIS COMPLETO - BUBBLE SORT')
print('=' * 70)
print()
print('SUMATORIAS (sin resolver):')
print('-' * 70)
print(f'Best:  {costs.total.best}')
print(f'Avg:   {costs.total.avg}')
print(f'Worst: {costs.total.worst}')
print()
print('EXPRESIONES SIMPLIFICADAS:')
print('-' * 70)
print(f'Best:  {solution.exact.best}')
print(f'Avg:   {solution.exact.avg}')
print(f'Worst: {solution.exact.worst}')
print()
print('NOTACIÓN BIG-O:')
print('-' * 70)
print(f'Best:  {solution.big_o.best}')
print(f'Avg:   {solution.big_o.avg}')
print(f'Worst: {solution.big_o.worst}')
print()
print('COTAS ASINTÓTICAS:')
print('-' * 70)
print(f'Ω (omega): {solution.bounds.omega}')
print(f'Θ (theta): {solution.bounds.theta}')
print(f'O (big-o): {solution.bounds.big_o}')
print()
print('=' * 70)
print('VERIFICACIÓN:')
print('=' * 70)

# Verificar fórmulas esperadas
import sympy as sp
n = sp.Symbol('n')

expected_best = n * (n - 1) / 2
expected_avg = sp.Rational(5, 4) * n * (n - 1)
expected_worst = 2 * n * (n - 1)

actual_best = sp.sympify(solution.exact.best)
actual_avg = sp.sympify(solution.exact.avg)
actual_worst = sp.sympify(solution.exact.worst)

print(f'✓ Best esperado:  {expected_best.expand()} = {sp.simplify(expected_best)}')
print(f'  Best obtenido:  {actual_best.expand()} = {sp.simplify(actual_best)}')
print(f'  Coincide: {sp.simplify(actual_best - expected_best) == 0}')
print()
print(f'✓ Avg esperado:   {expected_avg.expand()} = {sp.simplify(expected_avg)}')
print(f'  Avg obtenido:   {actual_avg.expand()} = {sp.simplify(actual_avg)}')
print(f'  Coincide: {sp.simplify(actual_avg - expected_avg) == 0}')
print()
print(f'✓ Worst esperado: {expected_worst.expand()} = {sp.simplify(expected_worst)}')
print(f'  Worst obtenido: {actual_worst.expand()} = {sp.simplify(actual_worst)}')
print(f'  Coincide: {sp.simplify(actual_worst - expected_worst) == 0}')
print()
