"""
Test para verificar que las expresiones de costos de loops se simplifican correctamente
"""
import requests
import json

pseudocode = """
ordenamiento_burbuja(A, n)
begin
    for i 🡨 1 to n do
    begin
        for j 🡨 1 to n do
        begin
            x 🡨 A[j]
        end
    end
end
"""

print("Analizando pseudocódigo con loops anidados...")
print("=" * 80)

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"text": pseudocode},
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    result = response.json()
    
    per_line = result.get("costs", {}).get("per_line", [])
    
    print("\nCOSTOS POR LÍNEA:")
    print("=" * 80)
    
    for line_cost in per_line:
        line_num = line_cost["line_number"]
        code = line_cost["code"].strip()
        cost = line_cost["cost"]
        
        print(f"\nLínea {line_num}: {code}")
        print(f"  Best:  {cost['best']}")
        
        # Verificar si hay expresiones sin simplificar
        for case in ['best', 'avg', 'worst']:
            cost_str = cost[case]
            
            # Buscar patrones de expresiones no simplificadas
            if "- 1 + 2" in cost_str or "- 1) + 2" in cost_str:
                print(f"\n  ⚠️  {case.upper()}: Expresión NO simplificada detectada")
                print(f"     {cost_str}")
            elif "((n" in cost_str and "))" in cost_str:
                # Paréntesis dobles innecesarios
                print(f"\n  ⚠️  {case.upper()}: Paréntesis dobles innecesarios")
                print(f"     {cost_str}")
    
    print("\n" + "=" * 80)
    print("VERIFICACIÓN DE SIMPLIFICACIÓN")
    print("=" * 80)
    
    # Buscar las líneas de los for loops
    for_lines = [lc for lc in per_line if any(op == 'For' for op in lc.get('operations', []))]
    
    if for_lines:
        print(f"\nEncontradas {len(for_lines)} líneas de loops:")
        all_simplified = True
        
        for line_cost in for_lines:
            line_num = line_cost["line_number"]
            cost = line_cost["cost"]["best"]
            
            # Verificar si está simplificado
            if "- 1 + 2" in cost or "- 1) + 2" in cost:
                print(f"\n  ❌ Línea {line_num}: NO simplificada")
                print(f"     {cost}")
                all_simplified = False
            else:
                print(f"\n  ✅ Línea {line_num}: Simplificada correctamente")
                print(f"     {cost}")
        
        if all_simplified:
            print("\n" + "=" * 80)
            print("✅ TODAS LAS EXPRESIONES ESTÁN SIMPLIFICADAS")
            print("=" * 80)
        else:
            print("\n" + "=" * 80)
            print("❌ ALGUNAS EXPRESIONES NO ESTÁN SIMPLIFICADAS")
            print("=" * 80)
            print("\nEjemplos esperados:")
            print("  ❌ ((n-1) - 1 + 2)")
            print("  ✅ n")
    else:
        print("\n⚠️  No se encontraron líneas de loops")

else:
    print(f"Error {response.status_code}")
    print(response.text)
