#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test SelectionSort pseudocode"""

import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.core.psc_parser import PseudocodeParser

code = """SelectionSort(A)
begin
    n 🡨 length(A)
    i, j, min_index, temp

    ► Recorre el arreglo para establecer el límite de la sublista ordenada
    for i 🡨 1 to n - 1 do
    begin
        ► Asume que el primer elemento de la sublista no ordenada es el mínimo
        min_index 🡨 i

        ► Itera sobre la sublista no ordenada para encontrar el mínimo real
        for j 🡨 i + 1 to n do
        begin
            if (A[j] < A[min_index]) then
            begin
                min_index 🡨 j
            end
        end

        ► Intercambia el elemento mínimo encontrado con el primer elemento de la sublista no ordenada
        if (min_index ≠ i) then
        begin
            temp 🡨 A[i]
            A[i] 🡨 A[min_index]
            A[min_index] 🡨 temp
        end
    end
end"""

try:
    parser = PseudocodeParser()
    result = parser.build(code)  # Cambiar a build() en lugar de parse()
    print("✅ Parse exitoso!")
    print(f"Funciones: {len(result.functions)}")
    if result.functions:
        func = result.functions[0]
        print(f"Nombre: {func.name}")
        print(f"Params: {[p.name for p in func.params]}")
        print(f"Body statements: {len(func.body.statements)}")
        print("\n🌳 AST en JSON:")
        import json
        from dataclasses import asdict
        print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
