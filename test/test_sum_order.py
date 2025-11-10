"""
Test para verificar que las sumatorias anidadas se resuelven en el orden correcto
(de adentro hacia afuera)
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.modules.solver.solver import SeriesSolver
from app.shared.models import CostExpr

def test_nested_sums_order():
    """
    Verifica que sumatorias anidadas se resuelven de adentro hacia afuera
    
    Ejemplo: Sum(Sum(1, (j, 1, n-i)), (i, 1, n-1))
    - Primero debe resolver: Sum(1, (j, 1, n-i)) = n-i
    - Luego debe resolver: Sum(n-i, (i, 1, n-1))
    """
    print("=" * 70)
    print("TEST: Orden de Resolución de Sumatorias Anidadas")
    print("=" * 70)
    
    # Expresión con sumatorias anidadas (típica de burbuja)
    nested_expr = "Sum(Sum(1, (j, 1, n-i)), (i, 1, n-1))"
    
    print(f"\n📝 Expresión: {nested_expr}")
    print("   (Sumatoria externa sobre i, interna sobre j)")
    
    # Crear expresión de costo
    cost_expr = CostExpr(
        best="0",
        avg="0",
        worst=nested_expr
    )
    
    # Resolver con pasos
    solver = SeriesSolver()
    solution = solver.solve(cost_expr, show_steps=True)
    
    print("\n" + "=" * 70)
    print("PASOS DE RESOLUCIÓN:")
    print("=" * 70)
    
    # Filtrar solo los pasos del peor caso
    worst_steps = [s for s in solution.steps if s.case == "worst"]
    
    for step in worst_steps:
        print(f"\n[Paso {step.step_number}] {step.description}")
        print(f"  {step.expression}")
    
    # Verificaciones
    print("\n" + "=" * 70)
    print("VERIFICACIONES:")
    print("=" * 70)
    
    # Buscar los pasos de resolución de sumatorias
    sum_steps = [s for s in worst_steps if "sumatoria" in s.description.lower() and "resolver" in s.description.lower()]
    
    if len(sum_steps) >= 2:
        first_step = sum_steps[0]
        second_step = sum_steps[1]
        
        print(f"\n1️⃣ Primer paso: {first_step.description}")
        print(f"   {first_step.expression}")
        
        # Verificar que el primer paso contiene (j, 1, n-i)
        if "(j" in first_step.expression and "n - i" in first_step.expression:
            print("   ✅ Correcto: Resuelve la sumatoria INTERNA (sobre j)")
        else:
            print("   ❌ Error: No resuelve la sumatoria interna primero")
        
        print(f"\n2️⃣ Segundo paso: {second_step.description}")
        print(f"   {second_step.expression}")
        
        # Verificar que el segundo paso contiene (i, 1, n-1)
        if "(i" in second_step.expression and "n - 1" in second_step.expression:
            print("   ✅ Correcto: Resuelve la sumatoria EXTERNA (sobre i)")
        else:
            print("   ❌ Error: No resuelve la sumatoria externa después")
        
        # Verificar descripciones
        print("\n📋 Descripciones:")
        if "interna" in first_step.description.lower():
            print("   ✅ Primera descripción indica 'interna'")
        else:
            print("   ⚠️  Primera descripción no menciona 'interna'")
        
        if "externa" in second_step.description.lower():
            print("   ✅ Segunda descripción indica 'externa'")
        else:
            print("   ⚠️  Segunda descripción no menciona 'externa'")
    else:
        print("   ❌ No se encontraron suficientes pasos de resolución")
    
    # Mostrar resultado final
    print("\n" + "=" * 70)
    print("RESULTADO FINAL:")
    print("=" * 70)
    print(f"✅ Expresión exacta: {solution.exact.worst}")
    print(f"✅ Big-O: {solution.big_o.worst}")
    print(f"✅ Cotas: {solution.bounds.theta}")

def test_triple_nested_sums():
    """
    Prueba con 3 niveles de anidamiento
    """
    print("\n\n" + "=" * 70)
    print("TEST: Triple Anidamiento")
    print("=" * 70)
    
    # Expresión con 3 sumatorias anidadas
    expr = "Sum(Sum(Sum(1, (k, 1, j)), (j, 1, i)), (i, 1, n))"
    
    print(f"\n📝 Expresión: {expr}")
    print("   (3 niveles: externa=i, media=j, interna=k)")
    
    cost_expr = CostExpr(
        best="0",
        avg="0",
        worst=expr
    )
    
    solver = SeriesSolver()
    solution = solver.solve(cost_expr, show_steps=True)
    
    worst_steps = [s for s in solution.steps if s.case == "worst"]
    sum_steps = [s for s in worst_steps if "sumatoria" in s.description.lower() and "resolver" in s.description.lower()]
    
    print("\n📋 Orden de Resolución:")
    for i, step in enumerate(sum_steps, 1):
        print(f"{i}. {step.description}")
        print(f"   Expresión: {step.expression[:80]}...")
    
    print(f"\n✅ Resultado final: {solution.exact.worst}")
    print(f"✅ Big-O: {solution.big_o.worst}")

if __name__ == "__main__":
    print("🧪 TEST: ORDEN DE RESOLUCIÓN DE SUMATORIAS\n")
    
    test_nested_sums_order()
    test_triple_nested_sums()
    
    print("\n" + "=" * 70)
    print("✅ TESTS COMPLETADOS")
    print("=" * 70)
