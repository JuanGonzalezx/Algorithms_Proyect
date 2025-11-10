"""Verificar los tres casos de coste"""
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

print('=' * 70)
print('COSTOS (sumatorias sin resolver):')
print('=' * 70)
print()
print('Best case: ', costs.total.best)
print()
print('Avg case:  ', costs.total.avg)
print()
print('Worst case:', costs.total.worst)
print()
