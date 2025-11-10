"""
Test directo de la función de simplificación
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.modules.analyzer.cost_model import CostAnalyzer

# Test de simplificación
test_cases = [
    ("(n) - (1) + 2", "n + 1"),
    ("((n-1)) - (1) + 2", "n"),
    ("(n - 1) - 1 + 2", "n"),
    ("n - 1 + 2", "n + 1"),
    ("((n - 1) - 1 + 2)", "n"),
]

print("Probando simplificación de expresiones:")
print("=" * 80)

all_passed = True

for input_expr, expected in test_cases:
    result = CostAnalyzer._simplify_expr(input_expr)
    passed = result == expected
    status = "✅" if passed else "❌"
    
    print(f"\n{status} Input:    {input_expr}")
    print(f"  Expected: {expected}")
    print(f"  Got:      {result}")
    
    if not passed:
        all_passed = False

print("\n" + "=" * 80)
if all_passed:
    print("✅ TODOS LOS TESTS PASARON")
else:
    print("❌ ALGUNOS TESTS FALLARON")
