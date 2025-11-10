#!/usr/bin/env python3
"""Test minimalista para el if-else del SelectionSort"""

from app.core.psc_parser import PseudocodeParser
import json
from dataclasses import asdict

code = """SelectionSort(A)
begin
    if (min_index ≠ i) then
    begin
        temp 🡨 A[i]
        A[i] 🡨 A[min_index]
        A[min_index] 🡨 temp
    end
end"""

try:
    parser = PseudocodeParser()
    result = parser.build(code)
    print("✅ Parse exitoso!")
    
    if_stmt = result.functions[0].body.statements[0]
    print(f"\nThen block statements: {len(if_stmt.then_block.statements)}")
    for i, stmt in enumerate(if_stmt.then_block.statements):
        print(f"  {i+1}. {type(stmt).__name__}")
    
    print("\n🌳 AST del if-else:")
    print(json.dumps(asdict(if_stmt), indent=2, ensure_ascii=False))
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
