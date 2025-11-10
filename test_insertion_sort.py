"""
Test para verificar el análisis de complejidad del ordenamiento por inserción.

El algoritmo de inserción tiene:
- Mejor caso: O(n) - array ya ordenado, while no entra al body
- Caso promedio: O(n²) - while itera i/2 veces en promedio
- Peor caso: O(n²) - array ordenado inversamente, while itera i veces
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.modules.syntax_validator.agent import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import get_cost_analyzer
from app.modules.solver.solver import get_series_solver
from app.shared.models import PseudocodeIn


def test_insertion_sort_complexity():
    """Test del análisis completo del ordenamiento por inserción."""
    
    pseudocode = """ordenamiento_por_insercion(A, n)
begin
    for i 🡨 2 to n do
    begin
        clave 🡨 A[i]
        j 🡨 i - 1
        while (j > 0 and A[j] > clave) do
        begin
            A[j+1] 🡨 A[j]
            j 🡨 j - 1
        end
        A[j+1] 🡨 clave
    end
end
"""
    
    print("=" * 80)
    print("TEST: Ordenamiento por Inserción")
    print("=" * 80)
    
    # Paso 1: Validación de sintaxis
    print("\n[1/4] Validando sintaxis...")
    validator = get_syntax_validator()
    input_data = PseudocodeIn(text=pseudocode, language_hint="es")
    validation = validator.validate(input_data)
    
    if not validation.era_algoritmo_valido:
        print(f"❌ Error de sintaxis: {validation.errores}")
        return False
    
    print("✅ Sintaxis válida")
    
    # Paso 2: Construcción del AST
    print("\n[2/4] Construyendo AST...")
    parser = get_parser_agent()
    try:
        ast_program = parser.parse(validation.codigo_corregido)
        print(f"✅ AST construido: {len(ast_program.functions)} función(es)")
    except Exception as e:
        print(f"❌ Error al construir AST: {e}")
        return False
    
    # Paso 3: Análisis de costos
    print("\n[3/4] Analizando costos...")
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast_program)
    
    print(f"✅ Nodos analizados: {len(costs.per_node)}")
    
    # Encontrar el nodo While
    while_node = None
    for node in costs.per_node:
        if node.node_type == "While":
            while_node = node
            break
    
    if not while_node:
        print("❌ No se encontró el nodo While")
        return False
    
    print(f"\n📊 Costo del While:")
    print(f"   Mejor caso:  {while_node.cost.best}")
    print(f"   Caso medio:  {while_node.cost.avg}")
    print(f"   Peor caso:   {while_node.cost.worst}")
    
    # Paso 4: Resolver sumatorias
    print("\n[4/4] Resolviendo sumatorias...")
    solver = get_series_solver()
    solution = solver.solve(costs.total, show_steps=False, per_line_costs=costs.per_line)
    
    print(f"\n📈 Complejidad Total:")
    print(f"   Mejor caso:  {solution.exact.best} → {solution.big_o.best}")
    print(f"   Caso medio:  {solution.exact.avg} → {solution.big_o.avg}")
    print(f"   Peor caso:   {solution.exact.worst} → {solution.big_o.worst}")
    
    # Verificación de resultados esperados
    print("\n" + "=" * 80)
    print("VERIFICACIÓN DE RESULTADOS")
    print("=" * 80)
    
    success = True
    
    # Verificar mejor caso: debe ser O(n)
    if solution.big_o.best != 'O(n)':
        print(f"❌ Mejor caso incorrecto: esperado O(n), obtenido {solution.big_o.best}")
        success = False
    else:
        print(f"✅ Mejor caso correcto: {solution.big_o.best}")
    
    # Verificar caso medio: debe ser O(n²)
    if solution.big_o.avg not in ['O(n**2)', 'O(n^2)']:
        print(f"❌ Caso medio incorrecto: esperado O(n²), obtenido {solution.big_o.avg}")
        success = False
    else:
        print(f"✅ Caso medio correcto: {solution.big_o.avg}")
    
    # Verificar peor caso: debe ser O(n²)
    if solution.big_o.worst not in ['O(n**2)', 'O(n^2)']:
        print(f"❌ Peor caso incorrecto: esperado O(n²), obtenido {solution.big_o.worst}")
        success = False
    else:
        print(f"✅ Peor caso correcto: {solution.big_o.worst}")
    
    # Verificar que el while use la variable del loop padre (i)
    print(f"\n🔍 Detalles del análisis del While:")
    print(f"   - Debe usar la variable 'i' del for externo")
    print(f"   - Mejor caso: solo evalúa condición (no entra al body)")
    print(f"   - Peor caso: itera hasta i veces")
    
    if 'i' in while_node.cost.worst or 'j' in while_node.cost.worst:
        print(f"   ✅ El while usa correctamente la variable del loop padre")
    else:
        print(f"   ⚠️  El while debería usar la variable 'i' del loop padre")
        print(f"   Costo actual (peor caso): {while_node.cost.worst}")
    
    print("\n" + "=" * 80)
    if success:
        print("✅ TODOS LOS TESTS PASARON")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
    print("=" * 80 + "\n")
    
    return success


if __name__ == "__main__":
    try:
        success = test_insertion_sort_complexity()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
