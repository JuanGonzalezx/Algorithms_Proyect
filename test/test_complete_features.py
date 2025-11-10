"""
Test completo de las nuevas características:
- Costos por línea (own_cost)
- Costos por bloque (cost)
- Proceso paso a paso del solver
"""
from app.modules.syntax_validator.agent import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import get_cost_analyzer
from app.modules.solver.solver import SeriesSolver

# Pseudocódigo de prueba: Bubble Sort
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

print("=" * 80)
print("TEST COMPLETO: COSTOS POR LÍNEA Y PROCESO DEL SOLVER")
print("=" * 80)
print()

# Paso 1: Validar
print("[1/4] Validando sintaxis...")
from app.shared.models import PseudocodeIn
validator = get_syntax_validator()
validation = validator.validate(PseudocodeIn(text=codigo))
print(f"[OK] Codigo valido: {validation.era_algoritmo_valido}")
print()

# Paso 2: Parsear
print("[2/4] Generando AST...")
parser = get_parser_agent()
ast = parser.parse(validation.codigo_corregido)
print(f"✓ AST generado: {len(ast.functions)} funciones")
print()

# Paso 3: Analizar costos
print("[3/4] Analizando costos...")
analyzer = get_cost_analyzer()
costs = analyzer.analyze(ast, validation.codigo_corregido)
print(f"✓ Costos analizados: {len(costs.per_node)} nodos, {len(costs.per_line)} líneas")
print()

# Mostrar costos por BLOQUE
print("=" * 80)
print("COSTOS POR BLOQUE (incluyen hijos)")
print("=" * 80)
print()

for node in costs.per_node:
    if node.line_start and node.node_type in ['For', 'If', 'While', 'Assign']:
        line_info = f"Línea {node.line_start}"
        if node.line_end and node.line_end != node.line_start:
            line_info += f"-{node.line_end}"
        
        print(f"📍 {node.node_type} ({node.node_id})")
        print(f"   {line_info}")
        if node.code_snippet:
            print(f"   Código: {node.code_snippet}")
        print(f"   Costo de bloque (worst): {node.cost.worst}")
        print()

# Mostrar costos por LÍNEA
print("=" * 80)
print("COSTOS POR LÍNEA (propios, sin hijos)")
print("=" * 80)
print()

for line_cost in costs.per_line:
    print(f"Línea {line_cost.line_number}: {line_cost.code.strip()}")
    print(f"   Operaciones: {', '.join(line_cost.operations)}")
    print(f"   Costo propio (worst): {line_cost.cost.worst}")
    print()

# Paso 4: Resolver sumatorias con pasos
print("=" * 80)
print("[4/4] Resolviendo sumatorias CON PROCESO PASO A PASO")
print("=" * 80)
print()

solver = SeriesSolver()
solution = solver.solve(costs.total, show_steps=True)

print(f"📝 PROCESO DE RESOLUCIÓN ({len(solution.steps)} pasos)")
print()

# Mostrar solo los pasos del peor caso para no saturar
worst_steps = [step for step in solution.steps if step.case == "worst"]

for step in worst_steps:
    print(f"Paso {step.step_number}: {step.description}")
    print(f"   {step.expression}")
    print()

print("=" * 80)
print("RESULTADOS FINALES")
print("=" * 80)
print()
print(f"📊 Best:  {solution.exact.best}")
print(f"📊 Avg:   {solution.exact.avg}")
print(f"📊 Worst: {solution.exact.worst}")
print()
print(f"🎯 Big-O:")
print(f"   Best:  {solution.big_o.best}")
print(f"   Avg:   {solution.big_o.avg}")
print(f"   Worst: {solution.big_o.worst}")
print()
print(f"📐 Cotas asintóticas:")
print(f"   Ω (omega): {solution.bounds.omega}")
print(f"   Θ (theta): {solution.bounds.theta}")
print(f"   O (big-o): {solution.bounds.big_o}")
print()

print("=" * 80)
print("COMPARACIÓN: Costos de bloque vs costos de línea")
print("=" * 80)
print()

# Mostrar el mapeo visual
lines = validation.codigo_corregido.split('\n')
line_map = {lc.line_number: lc for lc in costs.per_line}

for i, line in enumerate(lines, 1):
    line_str = f"{i:3d} | {line}"
    
    if i in line_map:
        lc = line_map[i]
        cost_str = f" → Costo: {lc.cost.worst}"
        print(f"{line_str}{cost_str}")
    else:
        print(line_str)

print()
print("✅ Test completo finalizado")
