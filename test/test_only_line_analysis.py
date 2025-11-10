"""
Test para verificar el análisis por línea (único método)
"""
import requests
import json

pseudocode = "bublesort"

print("Verificando análisis por línea...")
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
    
    # Verificar que NO haya análisis por bloques
    steps = solution.get("steps", [])
    steps_by_line = solution.get("steps_by_line", [])
    
    print("\n" + "="*80)
    print("VERIFICACIÓN DE MÉTODOS")
    print("="*80)
    print(f"Pasos por bloques (steps): {len(steps)}")
    print(f"Pasos por línea (steps_by_line): {len(steps_by_line)}")
    
    if len(steps) > 0:
        print("\n⚠️  ADVERTENCIA: Hay pasos del análisis por bloques")
        print("   (deberían estar vacíos)")
    else:
        print("\n✅ OK: No hay análisis por bloques")
    
    if len(steps_by_line) > 0:
        print("✅ OK: Hay análisis por línea")
    else:
        print("\n❌ ERROR: No hay pasos del análisis por línea")
    
    # Mostrar análisis por línea (best case)
    print("\n" + "="*80)
    print("ANÁLISIS POR LÍNEA (BEST CASE)")
    print("="*80)
    
    best_steps = [s for s in steps_by_line if s.get("case") == "best"]
    
    if len(best_steps) > 0:
        print(f"\nTotal de pasos: {len(best_steps)}")
        
        # Primera paso (fórmula)
        print("\n--- PASO 1: Fórmula inicial ---")
        print(f"{best_steps[0].get('description', '')}")
        print(f"{best_steps[0].get('expression', '')}")
        
        # Pasos 2-7 (cada línea)
        print("\n--- PASOS 2-7: Costos de cada línea ---")
        for step in best_steps[1:7]:
            print(f"\nPaso {step.get('step_number')}:")
            print(f"  {step.get('description', '')}")
            print(f"  {step.get('expression', '')}")
        
        # Último paso (resultado final)
        print("\n--- PASO FINAL: Resultado ---")
        final_step = best_steps[-1]
        print(f"Paso {final_step.get('step_number')}:")
        print(f"  {final_step.get('description', '')}")
        print(f"  {final_step.get('expression', '')}")
    
    # Verificar costos exactos
    print("\n" + "="*80)
    print("COSTOS EXACTOS")
    print("="*80)
    exact = solution.get("exact", {})
    print(f"Best:  {exact.get('best', 'N/A')}")
    print(f"Avg:   {exact.get('avg', 'N/A')}")
    print(f"Worst: {exact.get('worst', 'N/A')}")
    
    print("\n" + "="*80)
    print("BIG-O")
    print("="*80)
    big_o = solution.get("big_o", {})
    print(f"Best:  {big_o.get('best', 'N/A')}")
    print(f"Avg:   {big_o.get('avg', 'N/A')}")
    print(f"Worst: {big_o.get('worst', 'N/A')}")

else:
    print(f"Error {response.status_code}")
    print(response.text)
