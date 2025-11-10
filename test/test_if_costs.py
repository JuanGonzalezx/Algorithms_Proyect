"""
Test para verificar que los costos por línea respetan best/avg/worst en condicionales
"""
import requests
import json

# Pseudocódigo simple con un if dentro de un for
pseudocode = """
ordenamiento_burbuja(A, n)
begin
    for i 🡨 1 to n do
    begin
        for j 🡨 1 to n do
        begin
            x 🡨 A[j]
            if (x > 5) then
            begin
                temp 🡨 x
                A[j] 🡨 0
                A[j+1] 🡨 temp
            end
        end
    end
end
"""

# Hacer petición al API
response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"text": pseudocode},
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    result = response.json()
    
    print("=" * 80)
    print("COSTOS POR LÍNEA")
    print("=" * 80)
    
    per_line = result.get("costs", {}).get("per_line", [])
    
    for line_cost in per_line:
        line_num = line_cost["line_number"]
        code = line_cost["code"].strip()
        cost = line_cost["cost"]
        
        print(f"\nLínea {line_num}: {code}")
        print(f"  Best:  {cost['best']}")
        print(f"  Avg:   {cost['avg']}")
        print(f"  Worst: {cost['worst']}")
        
        # Verificar las líneas dentro del if (9, 10, 11)
        if line_num in [9, 10, 11]:
            if cost['best'] == "0":
                print("  ✓ Best case correcto (0)")
            else:
                print(f"  ✗ Best case debería ser 0, es: {cost['best']}")
            
            if "0.5" in cost['avg'] or "0.25" in cost['avg']:
                print("  ✓ Avg case correcto (con probabilidad)")
            else:
                print(f"  ✗ Avg case debería tener probabilidad, es: {cost['avg']}")
    
    print("\n" + "=" * 80)
    print("COSTO TOTAL")
    print("=" * 80)
    
    total = result.get("costs", {}).get("total", {})
    print(f"Best:  {total.get('best')}")
    print(f"Avg:   {total.get('avg')}")
    print(f"Worst: {total.get('worst')}")
    
else:
    print(f"Error {response.status_code}: {response.text}")
