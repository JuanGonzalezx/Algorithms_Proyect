#!/usr/bin/env python3
"""Debug del parsing del if-else"""

from lark import Lark
from pathlib import Path

GRAMMAR_PATH = Path("app/grammar/pseudocode.lark")

code = """SelectionSort(A)
begin
    if (min_index ≠ i) then
    begin
        temp 🡨 A[i]
        A[i] 🡨 A[min_index]
        A[min_index] 🡨 temp
    end
end"""

with open(GRAMMAR_PATH, 'r', encoding='utf-8') as f:
    grammar = f.read()

parser = Lark(grammar, start='start', parser='lalr')
tree = parser.parse(code)

print("🌳 Árbol Lark:")
print(tree.pretty())
