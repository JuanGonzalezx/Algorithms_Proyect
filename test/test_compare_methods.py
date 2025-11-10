"""
Test para comparar los resultados de ambos métodos:
1. Análisis por bloques (steps)
2. Análisis por línea (steps_by_line)
"""
import requests
import json

pseudocode = "bublesort"

print("Comparando ambos métodos de análisis...")
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
    
    # Método 1: Análisis por bloques
    steps = solution.get("steps", [])
    # Método 2: Análisis por línea
    steps_by_line = solution.get("steps_by_line", [])
    
    print("\n" + "="*80)
    print("MÉTODO 1: ANÁLISIS POR BLOQUES")
    print("="*80)
    
    # Mostrar resultado final del best case por bloques
    best_steps_blocks = [s for s in steps if s.get("case") == "best"]
    if best_steps_blocks:
        final_step = best_steps_blocks[-1]
        print(f"\nPaso final (best):")
        print(f"  {final_step.get('description', '')}")
        print(f"  {final_step.get('expression', '')}")
    
    print("\n" + "="*80)
    print("MÉTODO 2: ANÁLISIS POR LÍNEA")
    print("="*80)
    
    # Mostrar todos los pasos del best case por línea
    best_steps_lines = [s for s in steps_by_line if s.get("case") == "best"]
    
    print(f"\nTotal de pasos (best): {len(best_steps_lines)}")
    print("\nPrimeros 3 pasos:")
    for step in best_steps_lines[:3]:
        print(f"\nPaso {step.get('step_number')}:")
        print(f"  {step.get('description', '')}")
        print(f"  {step.get('expression', '')}")
    
    print("\nÚltimos 2 pasos:")
    for step in best_steps_lines[-2:]:
        print(f"\nPaso {step.get('step_number')}:")
        print(f"  {step.get('description', '')}")
        print(f"  {step.get('expression', '')}")
    
    print("\n" + "="*80)
    print("COMPARACIÓN DE RESULTADOS FINALES")
    print("="*80)
    
    if best_steps_blocks and best_steps_lines:
        final_blocks = best_steps_blocks[-1].get('expression', '')
        final_lines = best_steps_lines[-1].get('expression', '')
        
        print(f"\nMétodo por bloques: {final_blocks}")
        print(f"Método por línea:   {final_lines}")
        
        if final_blocks == final_lines:
            print("\n✅ [OK] Ambos métodos dan el mismo resultado")
        else:
            print("\n❌ [ERROR] Los métodos dan resultados diferentes")
            print("\nLa diferencia puede deberse a:")
            print("  - Inclusión de costos de evaluación de loops (For/While)")
            print("  - Diferentes simplificaciones algebraicas")
    
    # Mostrar costos exactos del solution
    print("\n" + "="*80)
    print("COSTOS EXACTOS (desde solution)")
    print("="*80)
    exact = solution.get("exact", {})
    print(f"\nBest:  {exact.get('best', '')}")
    print(f"Avg:   {exact.get('avg', '')}")
    print(f"Worst: {exact.get('worst', '')}")
    
else:
    print(f"Error {response.status_code}")
    print(response.text)
