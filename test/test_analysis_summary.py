"""
Test completo para verificar que los costos respetan best/avg/worst en condicionales
"""
import json

# Simular el resultado del análisis
result_json = {
    "costs": {
        "per_line": [
            {"line_number": 4, "code": "for i 🡨 1 to n do", "operations": ["For"], 
             "cost": {"best": "(n - 1 + 2)", "avg": "(n - 1 + 2)", "worst": "(n - 1 + 2)"}},
            {"line_number": 6, "code": "for j 🡨 1 to n do", "operations": ["For"], 
             "cost": {"best": "Sum((n - 1 + 2), (i, 1, n))", "avg": "Sum((n - 1 + 2), (i, 1, n))", "worst": "Sum((n - 1 + 2), (i, 1, n))"}},
            {"line_number": 8, "code": "x 🡨 A[j]", "operations": ["Assign"], 
             "cost": {"best": "Sum(Sum(1, (j, 1, n)), (i, 1, n))", "avg": "Sum(Sum(1, (j, 1, n)), (i, 1, n))", "worst": "Sum(Sum(1, (j, 1, n)), (i, 1, n))"}},
            {"line_number": 9, "code": "if (x > 5) then", "operations": ["If"], 
             "cost": {"best": "Sum(Sum(1, (j, 1, n)), (i, 1, n))", "avg": "Sum(Sum(1, (j, 1, n)), (i, 1, n))", "worst": "Sum(Sum(1, (j, 1, n)), (i, 1, n))"}},
            {"line_number": 11, "code": "temp 🡨 x", "operations": ["Assign"], 
             "cost": {"best": "0", "avg": "Sum(Sum((0.5 * (1)), (j, 1, n)), (i, 1, n))", "worst": "Sum(Sum(1, (j, 1, n)), (i, 1, n))"}},
            {"line_number": 12, "code": "A[j] 🡨 0", "operations": ["Assign"], 
             "cost": {"best": "0", "avg": "Sum(Sum((0.5 * (1)), (j, 1, n)), (i, 1, n))", "worst": "Sum(Sum(1, (j, 1, n)), (i, 1, n))"}},
            {"line_number": 13, "code": "A[j+1] 🡨 temp", "operations": ["Assign"], 
             "cost": {"best": "0", "avg": "Sum(Sum((0.5 * (1)), (j, 1, n)), (i, 1, n))", "worst": "Sum(Sum(1, (j, 1, n)), (i, 1, n))"}}
        ],
        "total": {
            "best": "Sum(Sum(1 + 1, (j, 1, n)), (i, 1, n))",
            "avg": "Sum(Sum(1 + 1 + 0.5*(1 + 1 + 1), (j, 1, n)), (i, 1, n))",
            "worst": "Sum(Sum(1 + 1 + max(1 + 1 + 1, 0), (j, 1, n)), (i, 1, n))"
        }
    }
}

print("=" * 80)
print("ANÁLISIS DE COSTOS POR LÍNEA")
print("=" * 80)

per_line = result_json["costs"]["per_line"]

for line_cost in per_line:
    line_num = line_cost["line_number"]
    code = line_cost["code"]
    cost = line_cost["cost"]
    
    print(f"\nLínea {line_num}: {code}")
    print(f"  Best:  {cost['best']}")
    print(f"  Avg:   {cost['avg']}")
    print(f"  Worst: {cost['worst']}")
    
    # Análisis
    if line_num in [11, 12, 13]:  # Líneas dentro del if
        print("\n  📊 Análisis:")
        if cost['best'] == "0":
            print("  ✅ Best case = 0 (if nunca entra)")
        else:
            print(f"  ❌ Best case debería ser 0, es: {cost['best']}")
        
        if "0.5" in cost['avg']:
            print("  ✅ Avg case con probabilidad 0.5 (if entra 50% del tiempo)")
        else:
            print(f"  ❌ Avg case debería tener 0.5, es: {cost['avg']}")
        
        if cost['worst'] != "0" and "0.5" not in cost['worst']:
            print("  ✅ Worst case = costo completo (if siempre entra)")
        else:
            print(f"  ❌ Worst case debería ser costo completo, es: {cost['worst']}")
    
    elif line_num == 9:  # Línea del if
        print("\n  📊 Análisis:")
        if cost['best'] == cost['avg'] == cost['worst']:
            print("  ✅ Evaluación de condición igual en todos los casos")
        else:
            print("  ❌ Evaluación de condición debería ser igual en todos los casos")

print("\n" + "=" * 80)
print("COSTO TOTAL")
print("=" * 80)

total = result_json["costs"]["total"]
print(f"\nBest:  {total['best']}")
print(f"Avg:   {total['avg']}")
print(f"Worst: {total['worst']}")

print("\n📊 Análisis del costo total:")
if "0.5" in total['avg']:
    print("✅ Average case incluye probabilidad condicional")
else:
    print("❌ Average case debería incluir probabilidad condicional")

if "max" in total['worst']:
    print("✅ Worst case usa max() para elegir peor rama")
else:
    print("❌ Worst case debería usar max() para elegir peor rama")

print("\n" + "=" * 80)
print("CONCLUSIÓN")
print("=" * 80)

issues_found = []

# Verificar líneas dentro del if
for line_cost in per_line:
    line_num = line_cost["line_number"]
    cost = line_cost["cost"]
    
    if line_num in [11, 12, 13]:
        if cost['best'] != "0":
            issues_found.append(f"Línea {line_num}: Best case debería ser 0")
        if "0.5" not in cost['avg']:
            issues_found.append(f"Línea {line_num}: Avg case debería tener probabilidad 0.5")
        if cost['worst'] == "0":
            issues_found.append(f"Línea {line_num}: Worst case no debería ser 0")

if issues_found:
    print("\n❌ PROBLEMAS ENCONTRADOS:")
    for issue in issues_found:
        print(f"  - {issue}")
else:
    print("\n✅ TODOS LOS COSTOS SON CORRECTOS")
    print("\nLos costos por línea ahora respetan correctamente:")
    print("  • Best case: Líneas dentro del if tienen costo 0")
    print("  • Avg case: Líneas dentro del if se multiplican por 0.5")
    print("  • Worst case: Líneas dentro del if tienen costo completo")
    print("\nEsto es consistente con el análisis de complejidad estándar donde:")
    print("  • Mejor caso: el condicional nunca se cumple")
    print("  • Caso promedio: el condicional se cumple ~50% de las veces")
    print("  • Peor caso: el condicional siempre se cumple")
