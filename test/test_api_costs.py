"""
Test del endpoint /api/v1/costs usando requests
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Código de prueba: Bubble Sort
code = """
procedimiento ordenamientoBurbuja(A, n)
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

print("=" * 60)
print("TEST ENDPOINT: POST /api/v1/costs")
print("=" * 60)

try:
    # Hacer petición al endpoint
    response = requests.post(
        f"{BASE_URL}/api/v1/costs",
        json={
            "text": code,
            "language_hint": "es"
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✓ Respuesta exitosa!\n")
        print("Costo total:")
        print(f"  Mejor caso: {result['total']['best']}")
        print(f"  Caso promedio: {result['total']['avg']}")
        print(f"  Peor caso: {result['total']['worst']}")
        print(f"\nNodos analizados: {len(result['per_node'])}")
        print("\nPrimeros 3 nodos:")
        for node in result['per_node'][:3]:
            print(f"  - {node['node_id']} ({node['node_type']}): {node['cost']['worst']}")
    else:
        print(f"\n✗ Error: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n✗ No se pudo conectar al servidor.")
    print("   Asegúrate de que el servidor esté corriendo:")
    print("   python -m uvicorn main:app --host 0.0.0.0 --port 8000")
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "=" * 60)
