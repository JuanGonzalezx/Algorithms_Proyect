"""
Test rápido para verificar si las expresiones de loops se simplifican
"""
import requests
import json
import sys
import os

pseudocode = "bublesort"

try:
    response = requests.post(
        "http://localhost:8000/api/v1/analyze",
        json={"text": pseudocode},
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        per_line = result.get("costs", {}).get("per_line", [])
        
        print("VERIFICACION DE SIMPLIFICACION")
        print("=" * 60)
        
        # Buscar líneas de loops (For)
        for_lines = [lc for lc in per_line if 'For' in lc.get('operations', [])]
        
        if for_lines:
            print(f"\nEncontradas {len(for_lines)} lineas de loops\n")
            
            all_ok = True
            for line_cost in for_lines:
                line_num = line_cost["line_number"]
                cost_best = line_cost["cost"]["best"]
                
                # Verificar si contiene "- 1 + 2" o similar
                if "- 1 + 2" in cost_best or "- 1) + 2" in cost_best:
                    print(f"X Linea {line_num}: NO simplificada")
                    print(f"  {cost_best}")
                    all_ok = False
                else:
                    print(f"OK Linea {line_num}: Simplificada")
                    print(f"  {cost_best}")
            
            print("\n" + "=" * 60)
            if all_ok:
                print("EXITO: Todas las expresiones simplificadas!")
            else:
                print("ERROR: Algunas expresiones sin simplificar")
        else:
            print("No se encontraron lineas de loops")
    else:
        print(f"Error {response.status_code}")
        print(response.text[:200])
        
except Exception as e:
    print(f"Error: {e}")
