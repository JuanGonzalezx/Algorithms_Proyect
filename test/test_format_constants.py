"""
Test para verificar que el paso a paso por línea incluya las constantes C1, C2, C3...
"""
import requests
import json

pseudocode = "bublesort"

print("Testing formato de pasos con constantes C1, C2, C3...")
print("=" * 80)

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"text": pseudocode},
    headers={"Content-Type": "application/json"},
    timeout=60
)

if response.status_code == 200:
    result = response.json()
    solution = result.get("solution", {})
    by_line_steps = solution.get("steps_by_line", [])
    
    # Mostrar solo los primeros pasos de cada caso
    cases = {"best": [], "avg": [], "worst": []}
    
    for step in by_line_steps:
        case = step.get("case", "")
        if case in cases:
            cases[case].append(step)
    
    print("\nPRIMEROS PASOS POR CASO:")
    print("=" * 80)
    
    for case_name in ["best", "avg", "worst"]:
        print(f"\n{case_name.upper()}:")
        print("-" * 80)
        
        steps = cases[case_name]
        
        # Mostrar los primeros 6 pasos
        for step in steps[:6]:
            desc = step["description"]
            expr = step["expression"]
            
            print(f"\nPaso {step['step_number']}: {desc}")
            print(f"  {expr}")
            
            # Verificar si el primer paso tiene formato correcto
            if step['step_number'] in [1, 12, 26]:  # Primeros pasos de cada caso
                if "C1" in expr and "C2" in expr:
                    print("  [OK] Formato correcto con constantes C1, C2, C3...")
                else:
                    print("  [ERROR] Faltan constantes C1, C2, C3...")
    
    print("\n" + "=" * 80)
    print("VERIFICACIÓN DE FORMATO")
    print("=" * 80)
    
    # Verificar que el primer paso de cada caso tenga constantes
    first_steps = [cases["best"][0], cases["avg"][0], cases["worst"][0]]
    
    all_correct = True
    for step in first_steps:
        expr = step["expression"]
        case = step["case"]
        
        if "C1" in expr and "*" in expr:
            print(f"[OK] {case.upper()}: Primer paso tiene formato C1*L1 + C2*L2 + ...")
        else:
            print(f"[ERROR] {case.upper()}: Primer paso NO tiene formato con constantes")
            all_correct = False
    
    if all_correct:
        print("\n" + "=" * 80)
        print("[EXITO] FORMATO CORRECTO: Todos los casos usan C1, C2, C3...")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("[ERROR] El formato no incluye constantes correctamente")
        print("=" * 80)

else:
    print(f"Error {response.status_code}")
    print(response.text[:500])
