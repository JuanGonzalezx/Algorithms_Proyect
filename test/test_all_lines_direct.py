import requests
import json

# Pseudocódigo de bublesort directo (basado en gramática)
pseudocode = """
bublesort(A[1..n])
begin
    for i 🡨 1 to n-1 do
    begin
        for j 🡨 1 to n-i do
        begin
            if (A[j] > A[j+1]) then
            begin
                temp 🡨 A[j]
                A[j] 🡨 A[j+1]
                A[j+1] 🡨 temp
            end
        end
    end
end
"""

url = "http://localhost:8000/api/v1/analyze"
payload = {
    "text": "bublesort"  # Usar lenguaje natural que Gemini puede normalizar
}

print("Verificando que TODAS las lineas se incluyan en el analisis...")
print("="*80)

try:
    response = requests.post(url, json=payload, timeout=30)
    
    if response.status_code != 200:
        print(f"Error {response.status_code}")
        print(response.text)
        exit(1)
    
    data = response.json()
    
    # Extraer per_line costs
    per_line = data.get("costs", {}).get("per_line", [])
    
    print("\nCOSTOS POR LINEA:")
    print("="*80)
    print(f"Total de lineas con costo: {len(per_line)}")
    for lc in per_line:
        line_num = lc.get("line")
        ops = ", ".join(lc.get("operations", []))
        desc = lc.get("description", "")
        print(f"  L{line_num}: {ops} - {desc}")
    
    # Extraer primer paso del caso best
    solution = data.get("solution", {})
    steps_best = [s for s in solution.get("steps_by_line", []) if s.get("case") == "best"]
    
    print("\n" + "="*80)
    print("PRIMER PASO (BEST):")
    print("="*80)
    if steps_best:
        first_step = steps_best[0]
        print(first_step.get("description", ""))
        print(first_step.get("expression", ""))
    
    # Verificar que todas las líneas estén en la fórmula
    print("\n" + "="*80)
    print("VERIFICACION:")
    print("="*80)
    
    formula = first_step.get("expression", "") if steps_best else ""
    
    # Contar líneas en la fórmula
    lines_in_formula = []
    for lc in per_line:
        line_num = lc.get("line")
        if f"L{line_num}" in formula:
            lines_in_formula.append(line_num)
    
    print(f"Lineas totales en el codigo: {len(per_line)}")
    print(f"Lineas en la formula T(n): {len(lines_in_formula)}")
    print()
    
    if len(lines_in_formula) == len(per_line):
        print("[EXITO] Todas las lineas incluidas en la formula!")
        print()
        print("Formula completa:")
        print(f"  {formula}")
    else:
        print("[ERROR] Faltan lineas en la formula")
        missing = [lc.get("line") for lc in per_line if lc.get("line") not in lines_in_formula]
        print(f"Lineas faltantes: {', '.join(f'L{ln}' for ln in missing)}")
        print()
        print("Lineas faltantes son:")
        for lc in per_line:
            if lc.get("line") not in lines_in_formula:
                line_num = lc.get("line")
                ops = ", ".join(lc.get("operations", []))
                desc = lc.get("description", "")
                print(f"  L{line_num}: {ops} - {desc}")
        exit(1)

except requests.exceptions.RequestException as e:
    print(f"Error de conexión: {e}")
    exit(1)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
