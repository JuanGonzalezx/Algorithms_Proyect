"""
Test para verificar que los pasos por línea sean diferentes para cada caso
"""
import requests
import json

# Pseudocódigo simple
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
    print("PASOS DE SOLUCIÓN POR LÍNEA")
    print("=" * 80)
    
    solution = result.get("solution", {})
    by_line_steps = solution.get("steps_by_line", [])
    
    # Agrupar pasos por caso
    steps_by_case = {"best": [], "avg": [], "worst": []}
    
    for step in by_line_steps:
        case = step.get("case", "unknown")
        if case in steps_by_case:
            steps_by_case[case].append(step)
    
    # Mostrar los primeros pasos de cada caso
    for case in ["best", "avg", "worst"]:
        print(f"\n{'=' * 80}")
        print(f"CASO: {case.upper()}")
        print(f"Total de pasos: {len(steps_by_case[case])}")
        print(f"{'=' * 80}")
        
        # Mostrar los primeros 10 pasos
        for step in steps_by_case[case][:10]:
            # Limpiar caracteres especiales para evitar problemas de encoding
            desc = step['description'].encode('ascii', 'ignore').decode('ascii')
            expr = step['expression'].encode('ascii', 'ignore').decode('ascii')
            print(f"\nPaso {step['step_number']}: {desc}")
            print(f"  {expr}")
    
    # Verificar si los pasos son diferentes entre casos
    print("\n" + "=" * 80)
    print("VERIFICACIÓN DE DIFERENCIAS")
    print("=" * 80)
    
    # Comparar el número total de pasos
    best_count = len(steps_by_case["best"])
    avg_count = len(steps_by_case["avg"])
    worst_count = len(steps_by_case["worst"])
    
    print(f"\nNúmero de pasos:")
    print(f"  Best:  {best_count}")
    print(f"  Avg:   {avg_count}")
    print(f"  Worst: {worst_count}")
    
    if best_count == avg_count == worst_count:
        print("\n⚠️  Los tres casos tienen el mismo número de pasos")
    else:
        print("\n✅ Los casos tienen diferente número de pasos")
    
    # Comparar expresiones de líneas específicas
    print("\nComparación de expresiones para líneas dentro del if:")
    
    # Buscar pasos que mencionan líneas específicas
    for line_num in [9, 10]:  # Líneas dentro del if
        print(f"\n  Línea {line_num}:")
        for case in ["best", "avg", "worst"]:
            # Buscar el paso que muestra esta línea
            line_step = None
            for step in steps_by_case[case]:
                if f"Línea {line_num}" in step.get("description", ""):
                    line_step = step
                    break
            
            if line_step:
                expr = line_step["expression"]
                # Extraer solo la parte del costo
                if "=" in expr:
                    cost_part = expr.split("=", 1)[1].strip()
                    print(f"    {case}: {cost_part}")
            else:
                print(f"    {case}: (no encontrada)")
    
    # Verificar si hay diferencias
    print("\n" + "=" * 80)
    has_differences = False
    
    # Comparar algunas expresiones clave
    for case1, case2 in [("best", "avg"), ("avg", "worst"), ("best", "worst")]:
        steps1 = [s["expression"] for s in steps_by_case[case1][:5]]
        steps2 = [s["expression"] for s in steps_by_case[case2][:5]]
        
        if steps1 != steps2:
            has_differences = True
            print(f"\n✅ {case1.upper()} y {case2.upper()} tienen expresiones diferentes")
            break
    
    if not has_differences:
        print("\n❌ PROBLEMA: Los tres casos tienen las mismas expresiones")
        print("   Los pasos deberían ser diferentes para best/avg/worst")
        print("\nEjemplo de lo que se espera:")
        print("  Best:  L9 = 0")
        print("  Avg:   L9 = Sum(Sum((0.5 * (1)), ...))")
        print("  Worst: L9 = Sum(Sum(1, ...))")
    
else:
    print(f"Error {response.status_code}: {response.text}")
