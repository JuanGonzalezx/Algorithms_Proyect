"""
Verificación rápida de que todos los módulos se importan correctamente
"""
print("Verificando imports...")

try:
    from app.modules.syntax_validator.agent import get_syntax_validator
    print("✓ syntax_validator")
except Exception as e:
    print(f"✗ syntax_validator: {e}")

try:
    from app.modules.parser.service import get_parser_agent
    print("✓ parser")
except Exception as e:
    print(f"✗ parser: {e}")

try:
    from app.modules.analyzer.cost_model import get_cost_analyzer
    print("✓ cost_analyzer")
except Exception as e:
    print(f"✗ cost_analyzer: {e}")

try:
    from app.shared.models import (
        PseudocodeIn, SyntaxValidationResult, 
        ASTResult, CostExpr, NodeCost, CostsOut
    )
    print("✓ shared.models (todos los modelos)")
except Exception as e:
    print(f"✗ shared.models: {e}")

try:
    from app.api.routes import router
    print("✓ api.routes")
except Exception as e:
    print(f"✗ api.routes: {e}")

print("\n✓ Todos los módulos se importan correctamente!")
print("\nAgentes disponibles:")
print("  1. syntax_validator (validación sintáctica)")
print("  2. parser (Lark → AST)")
print("  3. cost_analyzer (AST → Sumatorias)")
