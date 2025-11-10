"""
Debug: Verificar cómo SymPy parsea sumatorias anidadas
"""
import sympy as sp
from sympy import Sum, symbols

n, i, j, k = symbols('n i j k', positive=True, integer=True)

print("=" * 70)
print("DEBUG: Parsing de Sumatorias Anidadas")
print("=" * 70)

# Caso 1: String con Sum anidado
print("\n1️⃣ Parsing desde string:")
print("   Input: 'Sum(Sum(1, (j, 1, n-i)), (i, 1, n-1))'")

expr_str = "Sum(Sum(1, (j, 1, n-i)), (i, 1, n-1))"
expr = sp.sympify(expr_str)

print(f"   Resultado: {expr}")
print(f"   Tipo: {type(expr)}")
print(f"   Es Sum? {isinstance(expr, Sum)}")

if isinstance(expr, Sum):
    print(f"   Límites: {expr.limits}")
    print(f"   Función: {expr.function}")
    print(f"   Función es Sum? {isinstance(expr.function, Sum)}")

# Caso 2: Construcción directa (correcto)
print("\n2️⃣ Construcción directa (anidada):")
inner_sum = Sum(1, (j, 1, n-i))
outer_sum = Sum(inner_sum, (i, 1, n-1))

print(f"   Interna: {inner_sum}")
print(f"   Externa: {outer_sum}")
print(f"   Función de externa: {outer_sum.function}")
print(f"   Función es Sum? {isinstance(outer_sum.function, Sum)}")

# Resolver
print("\n3️⃣ Resolver paso a paso:")
print(f"   Interna resuelta: {inner_sum.doit()}")
print(f"   Externa resuelta: {outer_sum.doit()}")

# Caso 3: ¿Qué pasa si sympify recibe Sum(Sum())?
print("\n4️⃣ Verificar estructura del expr parseado:")

def print_tree(expr, indent=0):
    prefix = "  " * indent
    if isinstance(expr, Sum):
        print(f"{prefix}Sum:")
        print(f"{prefix}  límites: {expr.limits}")
        print(f"{prefix}  función:")
        print_tree(expr.function, indent + 2)
    else:
        print(f"{prefix}{expr} (tipo: {type(expr).__name__})")

print_tree(expr)

print("\n" + "=" * 70)
