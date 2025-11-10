# -*- coding: utf-8 -*-
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
from app.shared.models import PseudocodeIn

# Pseudocodigo de prueba: Bubble Sort
# Usando el simbolo correcto: 🡨 (U+1F868)
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
print("TEST COMPLETO: COSTOS POR LINEA Y PROCESO DEL SOLVER")
print("=" * 80)
print()

# Paso 1: Validar
print("[1/4] Validando sintaxis...")
validator = get_syntax_validator()
validation = validator.validate(PseudocodeIn(text=codigo))
print(f"[OK] Codigo valido: {validation.era_algoritmo_valido}")
print()

# Paso 2: Parsear
print("[2/4] Generando AST...")
parser = get_parser_agent()
ast = parser.parse(validation.codigo_corregido)
print(f"[OK] AST generado: {len(ast.functions)} funciones")
print()

# Paso 3: Analizar costos
print("[3/4] Analizando costos...")
from app.modules.analyzer.cost_model import CostAnalyzerAgent
analyzer_agent = CostAnalyzerAgent()
costs = analyzer_agent.analyze(ast, validation.codigo_corregido)
print(f"[OK] Costos analizados: {len(costs.per_node)} nodos, {len(costs.per_line)} lineas")
print()

# Mostrar costos por BLOQUE
print("=" * 80)
print("COSTOS POR BLOQUE (incluyen hijos)")
print("=" * 80)
print()

for node in costs.per_node:
    if node.line_start and node.node_type in ['For', 'If', 'While', 'Assign']:
        line_info = f"Linea {node.line_start}"
        if node.line_end and node.line_end != node.line_start:
            line_info += f"-{node.line_end}"
        
        print(f"[+] {node.node_type} ({node.node_id})")
        print(f"   {line_info}")
        print(f"   Costo de bloque (worst): {node.cost.worst}")
        if node.own_cost:
            print(f"   Costo propio (worst): {node.own_cost.worst}")
        print()

# Mostrar costos por LINEA
print("=" * 80)
print("COSTOS POR LINEA (propios, sin hijos)")
print("=" * 80)
print()

for line_cost in costs.per_line:
    print(f"Linea {line_cost.line_number}")
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

print(f"[NOTE] PROCESO DE RESOLUCION ({len(solution.steps)} pasos)")
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
print(f"[>] Best:  {solution.exact.best}")
print(f"[>] Avg:   {solution.exact.avg}")
print(f"[>] Worst: {solution.exact.worst}")
print()
print(f"[*] Big-O:")
print(f"   Best:  {solution.big_o.best}")
print(f"   Avg:   {solution.big_o.avg}")
print(f"   Worst: {solution.big_o.worst}")
print()
print(f"[~] Cotas asintoticas:")
print(f"   Omega: {solution.bounds.omega}")
print(f"   Theta: {solution.bounds.theta}")
print(f"   Big-O: {solution.bounds.big_o}")
print()

print("=" * 80)
print("COMPARACION: Costos de bloque vs costos de linea")
print("=" * 80)
print()

# Mostrar el mapeo visual
lines = validation.codigo_corregido.split('\n')
line_map = {lc.line_number: lc for lc in costs.per_line}

for i, line in enumerate(lines, 1):
    line_str = f"{i:3d} | {line}"
    
    if i in line_map:
        lc = line_map[i]
        cost_str = f" -> Costo: {lc.cost.worst}"
        print(f"{line_str}{cost_str}")
    else:
        print(line_str)

print()
print("[DONE] Test completo finalizado")
