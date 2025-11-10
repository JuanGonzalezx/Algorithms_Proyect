"""
Test con el ejemplo real de bublesort usando lenguaje natural
"""
import requests
import json

# Usar lenguaje natural como el usuario
natural_language = "bublesort"

print("Enviando petición al API con lenguaje natural: 'bublesort'")
print("=" * 80)

# Hacer petición al API
response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"text": natural_language},
    headers={"Content-Type": "application/json"},
    timeout=120  # 2 minutos de timeout
)

if response.status_code == 200:
    result = response.json()
    
    print("\n✅ Análisis completado exitosamente\n")
    print("=" * 80)
    print("COSTOS POR LÍNEA")
    print("=" * 80)
    
    per_line = result.get("costs", {}).get("per_line", [])
    
    # Mostrar todas las líneas
    for line_cost in per_line:
        line_num = line_cost["line_number"]
        code = line_cost["code"].strip()
        cost = line_cost["cost"]
        
        print(f"\nLínea {line_num}: {code}")
        print(f"  Best:  {cost['best']}")
        print(f"  Avg:   {cost['avg']}")
        print(f"  Worst: {cost['worst']}")
    
    print("\n" + "=" * 80)
    print("VERIFICACIÓN DE LÍNEAS DENTRO DEL IF")
    print("=" * 80)
    
    # Encontrar las líneas dentro de condicionales
    # Buscar líneas que tienen diferentes costos en best/avg/worst
    conditional_lines = []
    for line_cost in per_line:
        cost = line_cost["cost"]
        if cost['best'] != cost['worst']:
            conditional_lines.append(line_cost)
    
    if conditional_lines:
        print(f"\n✅ Encontradas {len(conditional_lines)} líneas con costos condicionales:")
        for line_cost in conditional_lines:
            line_num = line_cost["line_number"]
            code = line_cost["code"].strip()
            cost = line_cost["cost"]
            
            print(f"\n  Línea {line_num}: {code}")
            
            # Verificar que best sea 0 o menor que worst
            if cost['best'] == "0":
                print("    ✓ Best = 0 (condicional nunca se cumple)")
            else:
                print(f"    ⚠ Best = {cost['best']} (no es 0)")
            
            # Verificar que avg tenga probabilidad
            if "0.5" in cost['avg'] or "0.25" in cost['avg']:
                print("    ✓ Avg con probabilidad condicional")
            else:
                print(f"    ⚠ Avg sin probabilidad explícita")
            
            # Verificar que worst sea el costo completo
            if "0.5" not in cost['worst'] and cost['worst'] != "0":
                print("    ✓ Worst = costo completo")
            else:
                print(f"    ⚠ Worst parece incorrecto")
    else:
        print("\n❌ No se encontraron líneas con costos condicionales diferenciados")
        print("Esto podría indicar que el algoritmo no tiene condicionales,")
        print("o que no se aplicó correctamente la probabilidad condicional.")
    
    print("\n" + "=" * 80)
    print("COSTO TOTAL")
    print("=" * 80)
    
    total = result.get("costs", {}).get("total", {})
    print(f"\nBest:  {total.get('best')}")
    print(f"Avg:   {total.get('avg')}")
    print(f"Worst: {total.get('worst')}")
    
    # Verificar que los costos totales sean diferentes
    if total.get('best') != total.get('worst'):
        print("\n✅ Los costos totales varían según el caso (best/avg/worst)")
    else:
        print("\n⚠ Los costos totales son iguales en todos los casos")
    
else:
    print(f"\n❌ Error {response.status_code}")
    try:
        error_detail = response.json()
        print(f"Detalle: {json.dumps(error_detail, indent=2)}")
    except:
        print(f"Respuesta: {response.text}")
