from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import CostAnalyzerAgent

codigo = """bubble_sort(A)
begin
  n 🡨 length(A)
  for i 🡨 1 to n-1 do
  begin
    for j 🡨 1 to n-i do
    begin
      if (A[j] > A[j+1]) then
      begin
        temp 🡨 A[j]
      end
    end
  end
end
"""

parser = get_parser_agent()
ast = parser.parse(codigo)

analyzer = CostAnalyzerAgent()
costs = analyzer.analyze(ast, codigo)

print("Lineas con costos:")
for lc in costs.per_line:
    print(f"  L{lc.line_number}: ops={lc.operations}, worst={lc.cost.worst}")
