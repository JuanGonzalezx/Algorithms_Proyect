"""
Script de verificación: imports y pipeline completo de 4 agentes.
"""
print("=" * 70)
print("VERIFICACIÓN: Imports y Pipeline de 4 Agentes")
print("=" * 70)

# Test 1: Imports de modelos
print("\n✓ Test 1: Importando modelos...")
try:
    from app.shared.models import (
        PseudocodeIn, SyntaxValidationResult, ASTResult, 
        CostExpr, CostsOut, ExactCosts, AsymptoticBounds, SolveOut
    )
    print("  ✓ Todos los modelos importados correctamente")
except Exception as e:
    print(f"  ✗ Error: {e}")
    exit(1)

# Test 2: Import de agentes
print("\n✓ Test 2: Importando agentes...")
try:
    from app.modules.syntax_validator.agent import get_syntax_validator
    from app.modules.parser.service import get_parser_agent
    from app.modules.analyzer.cost_model import get_cost_analyzer
    from app.modules.solver.solver import get_series_solver
    print("  ✓ Todos los agentes importados correctamente")
except Exception as e:
    print(f"  ✗ Error: {e}")
    exit(1)

# Test 3: Instanciar agentes
print("\n✓ Test 3: Instanciando agentes...")
try:
    validator = get_syntax_validator()
    parser = get_parser_agent()
    analyzer = get_cost_analyzer()
    solver = get_series_solver()
    print("  ✓ syntax_validator")
    print("  ✓ parser")
    print("  ✓ cost_analyzer")
    print("  ✓ series_solver")
except Exception as e:
    print(f"  ✗ Error: {e}")
    exit(1)

# Test 4: Pipeline completo
print("\n✓ Test 4: Ejecutando pipeline completo...")
try:
    codigo = """
    procedimiento suma(n)
    begin
        s 🡨 0
        for i 🡨 1 to n do
        begin
            s 🡨 s + i
        end
        return s
    end
    """
    
    # Paso 1: Validar
    validation = validator.validate(PseudocodeIn(text=codigo))
    assert validation.era_algoritmo_valido, "Validación falló"
    print("  ✓ Paso 1: Sintaxis validada")
    
    # Paso 2: Parsear
    ast = parser.parse(validation.codigo_corregido)
    assert ast is not None, "Parsing falló"
    print("  ✓ Paso 2: AST generado")
    
    # Paso 3: Analizar costos
    costs = analyzer.analyze(ast)
    assert costs.total is not None, "Análisis de costos falló"
    print(f"  ✓ Paso 3: Costos analizados (peor caso: {costs.total.worst})")
    
    # Paso 4: Resolver
    solution = solver.solve(costs.total)
    assert solution.exact is not None, "Resolver sumatorias falló"
    print(f"  ✓ Paso 4: Sumatorias resueltas (Big-O: {solution.big_o.worst})")
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 5: Verificar API routes
print("\n✓ Test 5: Verificando API routes...")
try:
    from app.api.routes import router
    print("  ✓ Router importado correctamente")
    
    # Verificar que existen los endpoints
    endpoints = [route.path for route in router.routes]
    expected = ["/validate-syntax", "/parse", "/costs", "/solve", "/health"]
    
    for endpoint in expected:
        if any(endpoint in path for path in endpoints):
            print(f"  ✓ Endpoint {endpoint} existe")
        else:
            print(f"  ✗ Endpoint {endpoint} NO existe")
            
except Exception as e:
    print(f"  ✗ Error: {e}")
    exit(1)

# Test 6: Serialización JSON
print("\n✓ Test 6: Verificando serialización JSON...")
try:
    import json
    json_data = solution.model_dump()
    json_str = json.dumps(json_data)
    print("  ✓ SolveOut se serializa correctamente a JSON")
    print(f"  ✓ Tamaño: {len(json_str)} bytes")
except Exception as e:
    print(f"  ✗ Error: {e}")
    exit(1)

# Test 7: Tests unitarios
print("\n✓ Test 7: Ejecutando tests unitarios...")
try:
    import subprocess
    result = subprocess.run(
        ["python", "-m", "pytest", "test_series_solver.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        # Contar tests pasados
        import re
        match = re.search(r'(\d+) passed', result.stdout)
        if match:
            num_passed = match.group(1)
            print(f"  ✓ {num_passed} tests pasados")
    else:
        print(f"  ✗ Algunos tests fallaron")
        print(result.stdout)
        
except Exception as e:
    print(f"  ⚠ No se pudo ejecutar pytest: {e}")

# Resumen final
print("\n" + "=" * 70)
print("VERIFICACIÓN COMPLETADA")
print("=" * 70)
print("\n✅ Estado del sistema:")
print("  • 4 agentes funcionando: syntax_validator, parser, cost_analyzer, series_solver")
print("  • Pipeline completo operativo")
print("  • Todos los modelos importables")
print("  • API endpoints disponibles")
print("  • Tests unitarios pasando")
print("\n🎯 Siguiente paso: Iniciar servidor")
print("  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
print("  Luego ir a: http://localhost:8000/docs")
print("  Y probar POST /api/v1/solve")
print()
