#!/usr/bin/env python3
"""Test simple de asignación a array"""

from lark import Lark
from pathlib import Path

GRAMMAR_PATH = Path("app/grammar/pseudocode.lark")

# Test 1: Asignación simple
code1 = """procedimiento test(A)
begin
    A[i] 🡨 valor
end"""

# Test 2: Asignación de array a array
code2 = """procedimiento test(A)
begin
    A[i] 🡨 A[j]
end"""

with open(GRAMMAR_PATH, 'r', encoding='utf-8') as f:
    grammar = f.read()

parser = Lark(grammar, start='start', parser='lalr')

print("=" * 60)
print("Test 1: A[i] 🡨 valor")
print("=" * 60)
tree1 = parser.parse(code1)
print(tree1.pretty())

print("\n" + "=" * 60)
print("Test 2: A[i] 🡨 A[j]")
print("=" * 60)
tree2 = parser.parse(code2)
print(tree2.pretty())
