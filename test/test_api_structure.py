"""
Test para ver la estructura completa de la respuesta del API
"""
import requests
import json

pseudocode = """
ordenamiento_burbuja(A, n)
begin
    for i 🡨 1 to n do
    begin
        x 🡨 A[i]
        if (x > 5) then
        begin
            y 🡨 x
        end
    end
end
"""

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"text": pseudocode},
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    result = response.json()
    
    # Guardar la respuesta completa
    with open("api_response_debug.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("✅ Respuesta guardada en api_response_debug.json")
    
    # Mostrar estructura de solutions
    solutions = result.get("solutions", {})
    print("\n" + "=" * 80)
    print("ESTRUCTURA DE SOLUTIONS")
    print("=" * 80)
    
    print(f"\nClaves en solutions: {list(solutions.keys())}")
    
    if "by_line" in solutions:
        by_line = solutions["by_line"]
        print(f"\nClaves en by_line: {list(by_line.keys())}")
        
        if "steps" in by_line:
            steps = by_line["steps"]
            print(f"\nNúmero total de pasos: {len(steps)}")
            
            if steps:
                print(f"\nPrimer paso:")
                print(json.dumps(steps[0], indent=2))
                
                # Ver si hay campo 'case'
                if "case" in steps[0]:
                    print("\n✅ Los pasos tienen campo 'case'")
                else:
                    print("\n❌ Los pasos NO tienen campo 'case'")
                    print(f"Campos disponibles: {list(steps[0].keys())}")
                
                # Mostrar los primeros 5 pasos
                print(f"\nPrimeros 5 pasos:")
                for i, step in enumerate(steps[:5]):
                    case = step.get("case", "NO CASE")
                    print(f"\n{i+1}. [{case}] {step.get('description', 'NO DESC')}")
                    print(f"   {step.get('expression', 'NO EXPR')}")
        else:
            print("\n❌ No hay campo 'steps' en by_line")
    else:
        print("\n❌ No hay campo 'by_line' en solutions")
else:
    print(f"Error {response.status_code}: {response.text}")
