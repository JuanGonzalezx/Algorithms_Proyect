#!/usr/bin/env python3
"""Debug del if-else del factorial"""

from lark import Lark
from pathlib import Path

GRAMMAR_PATH = Path("app/grammar/pseudocode.lark")

code = """procedimiento factorial(n)
begin
    if n ≤ 1 then
    begin
        return 1
    end
    else
    begin
        return n * factorial(n - 1)
    end
end"""

with open(GRAMMAR_PATH, 'r', encoding='utf-8') as f:
    grammar = f.read()

parser = Lark(grammar, start='start', parser='lalr')
tree = parser.parse(code)

print("🌳 Árbol Lark del factorial:")
print(tree.pretty())
