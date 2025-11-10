# Test simple para debug de costos por linea
from app.modules.syntax_validator.agent import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import CostAnalyzerAgent
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
            end
        end
    end
end
"""

print("=== DEBUG: Costos por linea ===\n")

# Validar
validator = get_syntax_validator()
validation = validator.validate(PseudocodeIn(text=codigo))

# Parsear
parser = get_parser_agent()
ast = parser.parse(validation.codigo_corregido)

# Analizar
analyzer = CostAnalyzerAgent()
costs = analyzer.analyze(ast, validation.codigo_corregido)

print(f"Total nodos: {len(costs.per_node)}")
print(f"Total lineas con costo: {len(costs.per_line)}\n")

print("=== NODOS POR BLOQUE ===")
for node in costs.per_node:
    if node.line_start:
        print(f"{node.node_type:10s} Linea {node.line_start:2d}  Cost(worst)={node.cost.worst}")
        if node.own_cost:
            print(f"           {' '*9}  Own(worst)={node.own_cost.worst}")

print("\n=== COSTOS POR LINEA ===")
for lc in costs.per_line:
    print(f"Linea {lc.line_number:2d}: {lc.operations[0]:10s}  Cost={lc.cost.worst}")

print(f"\n=== TOTAL ===")
print(f"Worst: {costs.total.worst}")
