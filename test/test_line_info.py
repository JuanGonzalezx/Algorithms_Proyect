"""Test para verificar información de línea en los costos"""
from app.modules.syntax_validator.agent import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import get_cost_analyzer
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

print('=' * 80)
print('COSTOS CON INFORMACIÓN DE LÍNEA')
print('=' * 80)
print()

# Mostrar cada nodo con su información de línea
for node in costs.per_node:
    print(f'📍 {node.node_type} ({node.node_id})')
    print(f'   Línea: {node.line_start}' + (f'-{node.line_end}' if node.line_end and node.line_end != node.line_start else '') if node.line_start else '   Línea: N/A')
    if node.code_snippet:
        print(f'   Código: {node.code_snippet}')
    print(f'   Costo (worst): {node.cost.worst}')
    print()

print('=' * 80)
print('CÓDIGO FUENTE CON NÚMEROS DE LÍNEA')
print('=' * 80)
print()

lines = codigo.split('\n')
for i, line in enumerate(lines, 1):
    print(f'{i:3d} | {line}')

print()
print('=' * 80)
print('MAPEO PARA FRONTEND')
print('=' * 80)
print()

# Crear un mapeo línea -> costo para el frontend
line_costs = {}
for node in costs.per_node:
    if node.line_start and node.node_type in ['For', 'While', 'If', 'Assign']:
        if node.line_start not in line_costs:
            line_costs[node.line_start] = []
        line_costs[node.line_start].append({
            'type': node.node_type,
            'cost': node.cost.worst,
            'snippet': node.code_snippet
        })

# Mostrar el mapeo
for line_num in sorted(line_costs.keys()):
    print(f'Línea {line_num}:')
    for item in line_costs[line_num]:
        print(f'  • [{item["type"]}] {item["cost"]}')
        if item['snippet']:
            print(f'    "{item["snippet"]}"')
    print()
