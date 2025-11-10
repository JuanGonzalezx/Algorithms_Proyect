"""
Test para ver los costos de cada línea incluyendo For loops
"""
import requests
import json

pseudocode = "bublesort"

print("Verificando costos de cada línea...")
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
    
    print("\nCOSTOS DETALLADOS POR LÍNEA:")
    print("="*80)
    
    for lc in per_line:
        line_num = lc.get("line")
        ops = ", ".join(lc.get("operations", []))
        desc = lc.get("description", "")
        cost = lc.get("cost", {})
        
        print(f"\nL{line_num}: {ops}")
        print(f"  Descripción: {desc}")
        print(f"  Cost.best:  {cost.get('best', 'N/A')}")
        print(f"  Cost.avg:   {cost.get('avg', 'N/A')}")
        print(f"  Cost.worst: {cost.get('worst', 'N/A')}")
    
    # Calcular suma manual
    print("\n" + "="*80)
    print("SUMA MANUAL DE COSTOS (BEST CASE):")
    print("="*80)
    
    total_expr = []
    for lc in per_line:
        line_num = lc.get("line")
        cost_best = lc.get("cost", {}).get("best", "0")
        if cost_best and cost_best != "0":
            total_expr.append(f"L{line_num}: {cost_best}")
    
    for expr in total_expr:
        print(f"  {expr}")
    
else:
    print(f"Error {response.status_code}")
    print(response.text)
