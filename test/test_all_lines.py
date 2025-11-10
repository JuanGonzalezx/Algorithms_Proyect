"""
Test para verificar que TODAS las líneas se incluyen en el análisis por línea
"""
import requests
import json

pseudocode = "bublesort"

print("Verificando que TODAS las lineas se incluyan en el analisis...")
print("=" * 80)

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"text": pseudocode},
    headers={"Content-Type": "application/json"},
    timeout=60
)

if response.status_code == 200:
    result = response.json()
    
    # Obtener costos por línea
    per_line = result.get("costs", {}).get("per_line", [])
    
    # Obtener pasos de solución por línea
    solution = result.get("solution", {})
    by_line_steps = solution.get("steps_by_line", [])
    
    print(f"\nCOSTOS POR LINEA:")
    print("=" * 80)
    print(f"Total de lineas con costo: {len(per_line)}")
    
    for lc in per_line:
        line_num = lc["line_number"]
        code = lc["code"].strip()[:50]
        ops = lc.get("operations", [])
        print(f"  L{line_num}: {ops[0] if ops else 'N/A'} - {code}")
    
    # Buscar el primer paso del caso BEST
    first_step = None
    for step in by_line_steps:
        if step.get("case") == "best":
            first_step = step
            break
    
    if first_step:
        expr = first_step["expression"]
        print(f"\n" + "=" * 80)
        print("PRIMER PASO (BEST):")
        print("=" * 80)
        print(f"{first_step['description']}")
        print(f"{expr}")
        
        # Contar cuántas líneas aparecen en la fórmula
        lines_in_formula = []
        for lc in per_line:
            line_num = lc["line_number"]
            if f"L{line_num}" in expr:
                lines_in_formula.append(line_num)
        
        print(f"\n" + "=" * 80)
        print("VERIFICACION:")
        print("=" * 80)
        print(f"Lineas totales en el codigo: {len(per_line)}")
        print(f"Lineas en la formula T(n): {len(lines_in_formula)}")
        
        if len(lines_in_formula) == len(per_line):
            print("\n[OK] TODAS las lineas estan incluidas en la formula")
            print(f"Formula incluye: L{', L'.join(map(str, lines_in_formula))}")
        else:
            print("\n[ERROR] Faltan lineas en la formula")
            all_lines = set(lc["line_number"] for lc in per_line)
            missing = all_lines - set(lines_in_formula)
            print(f"Lineas faltantes: L{', L'.join(map(str, sorted(missing)))}")
            
            # Mostrar qué tipo de líneas faltan
            print("\nLineas faltantes son:")
            for line_num in sorted(missing):
                lc = next(l for l in per_line if l["line_number"] == line_num)
                ops = lc.get("operations", [])
                code = lc["code"].strip()[:50]
                print(f"  L{line_num}: {ops[0] if ops else 'N/A'} - {code}")
    else:
        print("\n[ERROR] No se encontro el primer paso")

else:
    print(f"Error {response.status_code}")
    print(response.text[:500])
