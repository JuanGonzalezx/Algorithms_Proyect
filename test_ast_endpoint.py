#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test del endpoint /ast solo con pseudocódigo"""

import sys
import io
import requests
import json

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000/api/v1"

# Ejemplo 1: Pseudocódigo simple
pseudocode_simple = """
procedimiento suma(a, b)
begin
    return a + b
end
"""

# Ejemplo 2: SelectionSort completo
pseudocode_selection = """
SelectionSort(A)
begin
    n 🡨 length(A)
    i, j, min_index, temp

    ► Recorre el arreglo
    for i 🡨 1 to n - 1 do
    begin
        min_index 🡨 i
        
        for j 🡨 i + 1 to n do
        begin
            if (A[j] < A[min_index]) then
            begin
                min_index 🡨 j
            end
        end
        
        if (min_index ≠ i) then
        begin
            temp 🡨 A[i]
            A[i] 🡨 A[min_index]
            A[min_index] 🡨 temp
        end
    end
end
"""

print("=" * 70)
print("🧪 PROBANDO ENDPOINT /ast (SOLO PSEUDOCÓDIGO)")
print("=" * 70)

# Test 1: Suma simple
print("\n📝 Test 1: Suma simple")
print("-" * 70)
try:
    response = requests.post(
        f"{BASE_URL}/ast",
        json={"content": pseudocode_simple},
        timeout=10
    )
    
    if response.status_code == 200:
        print("✅ SUCCESS")
        ast = response.json()["ast"]
        print(f"Funciones: {len(ast['functions'])}")
        print(f"Nombre: {ast['functions'][0]['name']}")
        print(f"Params: {[p['name'] for p in ast['functions'][0]['params']]}")
    else:
        print(f"❌ ERROR {response.status_code}")
        print(response.json())
except Exception as e:
    print(f"❌ EXCEPTION: {e}")

# Test 2: SelectionSort
print("\n📝 Test 2: SelectionSort completo")
print("-" * 70)
try:
    response = requests.post(
        f"{BASE_URL}/ast",
        json={"content": pseudocode_selection},
        timeout=10
    )
    
    if response.status_code == 200:
        print("✅ SUCCESS")
        ast = response.json()["ast"]
        func = ast['functions'][0]
        print(f"Funciones: {len(ast['functions'])}")
        print(f"Nombre: {func['name']}")
        print(f"Params: {[p['name'] for p in func['params']]}")
        print(f"Statements en body: {len(func['body']['statements'])}")
        
        # Mostrar estructura
        for i, stmt in enumerate(func['body']['statements'], 1):
            print(f"  Statement {i}: {stmt.get('type', 'Unknown')}")
    else:
        print(f"❌ ERROR {response.status_code}")
        print(response.json())
except Exception as e:
    print(f"❌ EXCEPTION: {e}")

print("\n" + "=" * 70)
print("✅ Tests completados")
print("=" * 70)
