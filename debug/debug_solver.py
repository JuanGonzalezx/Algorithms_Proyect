"""Debug: Ver qué sumatorias genera el cost_analyzer para Bubble Sort."""
from app.modules.syntax_validator.agent import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import get_cost_analyzer
from app.shared.models import PseudocodeIn

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

validator = get_syntax_validator()
validation = validator.validate(PseudocodeIn(text=codigo))

parser = get_parser_agent()
ast = parser.parse(validation.codigo_corregido)

analyzer = get_cost_analyzer()
costs = analyzer.analyze(ast)

print("=" * 70)
print("SUMATORIAS GENERADAS POR COST_ANALYZER")
print("=" * 70)

print(f"\nMejor caso:  {costs.total.best}")
print(f"Caso avg:    {costs.total.avg}")
print(f"Peor caso:   {costs.total.worst}")

print("\n" + "=" * 70)
print("RESOLVIENDO CON SYMPY")
print("=" * 70)

import sympy as sp
from sympy import symbols, Sum, simplify, sympify, Max

n = symbols('n', positive=True, integer=True)
i = symbols('i', positive=True, integer=True)
j = symbols('j', positive=True, integer=True)
k = symbols('k', positive=True, integer=True)

# Parsear la expresión del peor caso
expr_str = costs.total.worst
print(f"\nExpresión original: {expr_str}")

# Crear namespace
namespace = {
    'n': n,
    'i': i,
    'j': j,
    'k': k,
    'Sum': Sum,
    'Max': Max,
    'max': Max,
}

# Parsear
expr = sympify(expr_str, locals=namespace)
print(f"Parseada: {expr}")

# Resolver
resolved = expr.doit()
print(f"Resuelta (.doit()): {resolved}")

# Simplificar
simplified = simplify(resolved)
print(f"Simplificada: {simplified}")

# Expandir
expanded = sp.expand(simplified)
print(f"Expandida: {expanded}")

print("\n" + "=" * 70)
print("ANÁLISIS")
print("=" * 70)

print(f"\nVariables libres: {expanded.free_symbols}")
print(f"Tiene 'i'?: {i in expanded.free_symbols}")
print(f"Tiene 'n'?: {n in expanded.free_symbols}")

# Intentar factorizar en términos de n
if i in expanded.free_symbols:
    print("\n⚠️ PROBLEMA: La expresión todavía tiene 'i'")
    print("Esto significa que la sumatoria externa no se resolvió correctamente")
