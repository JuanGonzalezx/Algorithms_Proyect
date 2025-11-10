#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test final: Verificar endpoint completo con todas las líneas
"""

import requests
import json

# URL del endpoint
url = "http://localhost:8000/api/v1/analyze"

# Datos de prueba
data = {
    "text": "ordenamiento burbuja",
    "language_hint": "es"
}

print("=" * 80)
print("TEST: Endpoint completo /api/v1/analyze")
print("=" * 80)
print()
print(f"Input: {data['text']}")
print()

try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    result = response.json()
    
    print(f"✅ Status: {response.status_code}")
    print()
    
    # Mostrar líneas
    per_line = result.get("costs", {}).get("per_line", [])
    print(f"Total líneas en per_line: {len(per_line)}")
    print()
    
    print("=" * 80)
    print("COSTOS POR LÍNEA")
    print("=" * 80)
    print()
    
    for lc in per_line:
        line_num = lc["line_number"]
        code = lc["code"].strip()
        ops = ", ".join(lc["operations"])
        cost_worst = lc["cost"]["worst"]
        
        print(f"Línea {line_num:2d}: {code}")
        print(f"  Operaciones: {ops}")
        print(f"  Costo (worst): {cost_worst}")
        print()
    
    # Mostrar resultado final
    solution = result.get("solution", {})
    print("=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)
    print()
    print(f"Exact (worst): {solution.get('exact', {}).get('worst')}")
    print(f"Big-O: {solution.get('big_o', {}).get('worst')}")
    print()
    
    print("✅ Test completado exitosamente!")
    
except requests.exceptions.ConnectionError:
    print("❌ ERROR: No se pudo conectar al servidor")
    print("   Por favor ejecuta: uvicorn main:app --port 8000")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
