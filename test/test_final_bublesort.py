"""
Test final con bublesort para verificar que los pasos sean diferentes por caso
"""
import requests
import json

pseudocode = "bublesort"

print("Analizando:", pseudocode)
print("=" * 80)

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"text": pseudocode},
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    result = response.json()
    
    solution = result.get("solution", {})
    by_line_steps = solution.get("steps_by_line", [])
    
    # Agrupar pasos por caso
    steps_by_case = {"best": [], "avg": [], "worst": []}
    
    for step in by_line_steps:
        case = step.get("case", "unknown")
        if case in steps_by_case:
            steps_by_case[case].append(step)
    
    print(f"\nTotal de pasos por caso:")
    print(f"  Best:  {len(steps_by_case['best'])}")
    print(f"  Avg:   {len(steps_by_case['avg'])}")
    print(f"  Worst: {len(steps_by_case['worst'])}")
    
    # Mostrar pasos clave de cada caso
    print("\n" + "=" * 80)
    print("PASOS CLAVE POR CASO")
    print("=" * 80)
    
    for case in ["best", "avg", "worst"]:
        print(f"\n{case.upper()}:")
        case_steps = steps_by_case[case]
        
        # Mostrar paso de línea dentro del if
        for step in case_steps:
            desc = step["description"]
            if "Línea 9" in desc or "Linea 9" in desc:  # Primera línea dentro del if
                print(f"  {desc}")
                print(f"    {step['expression']}")
                break
        
        # Mostrar paso de sustitución de valores
        for step in case_steps:
            if "Sustituir valores" in step["description"]:
                expr = step["expression"]
                # Truncar si es muy largo
                if len(expr) > 100:
                    expr = expr[:100] + "..."
                print(f"  Sustituir valores:")
                print(f"    {expr}")
                break
        
        # Mostrar paso final
        for step in reversed(case_steps):
            if "final" in step["description"].lower():
                print(f"  Resultado final:")
                print(f"    {step['expression']}")
                break
    
    # Verificación de diferencias
    print("\n" + "=" * 80)
    print("VERIFICACIÓN")
    print("=" * 80)
    
    # Extraer expresiones de líneas dentro del if
    line_costs_by_case = {}
    for case in ["best", "avg", "worst"]:
        for step in steps_by_case[case]:
            if "Línea 9" in step["description"] or "Linea 9" in step["description"]:
                line_costs_by_case[case] = step["expression"]
                break
    
    print("\nCostos de Línea 9 (primera línea dentro del if):")
    for case in ["best", "avg", "worst"]:
        if case in line_costs_by_case:
            cost = line_costs_by_case[case]
            # Extraer solo la parte del costo
            if "=" in cost:
                cost = cost.split("=")[-1].strip()
            print(f"  {case}: {cost}")
    
    # Verificar si son diferentes
    if len(set(line_costs_by_case.values())) == 1:
        print("\n❌ PROBLEMA: Las líneas dentro del if tienen el mismo costo en todos los casos")
    elif len(set(line_costs_by_case.values())) == 3:
        print("\n✅ CORRECTO: Las líneas dentro del if tienen costos diferentes para cada caso")
    else:
        print("\n⚠️  PARCIAL: Algunos casos tienen costos diferentes")
    
    # Verificar resultados finales
    final_results = {}
    for case in ["best", "avg", "worst"]:
        for step in reversed(steps_by_case[case]):
            if "final" in step["description"].lower():
                expr = step["expression"]
                if "=" in expr:
                    final_results[case] = expr.split("=")[-1].strip()
                break
    
    print("\nResultados finales:")
    for case in ["best", "avg", "worst"]:
        if case in final_results:
            print(f"  {case}: {final_results[case]}")
    
    if len(set(final_results.values())) == 3:
        print("\n✅ Los tres casos tienen resultados finales diferentes")
    elif len(set(final_results.values())) == 1:
        print("\n❌ Los tres casos tienen el mismo resultado final")
    else:
        print("\n⚠️  Algunos casos tienen resultados iguales")
    
else:
    print(f"Error {response.status_code}")
    print(response.text)
