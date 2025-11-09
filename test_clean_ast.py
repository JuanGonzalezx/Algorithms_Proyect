"""Script para verificar que el AST ya no incluye campos line y col"""
from app.core.psc_parser import PseudocodeParser
import json

bubblesort_code = """
procedimiento BubbleSort(A, n)
begin
    for i 🡨 0 to n-1 do
    begin
        for j 🡨 0 to n-i-2 do
        begin
            if A[j] > A[j+1] then
            begin
                temp 🡨 A[j]
                A[j] 🡨 A[j+1]
                A[j+1] 🡨 temp
            end
        end
    end
end
"""

parser = PseudocodeParser()
ast = parser.build(bubblesort_code)

# Convertir a dict y mostrar
ast_dict = ast.to_dict()
print(json.dumps(ast_dict, indent=2, ensure_ascii=False))

# Verificar que no hay campos line o col
ast_str = json.dumps(ast_dict)
if '"line"' in ast_str or '"col"' in ast_str:
    print("\n❌ ERROR: Todavía existen campos 'line' o 'col' en el AST")
else:
    print("\n✅ ÉXITO: El AST ya no contiene campos 'line' ni 'col'")
