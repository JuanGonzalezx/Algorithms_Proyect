from app.modules.parser.service import get_parser_agent

code = """
procedimiento suma(a, b)
begin
    resultado 🡨 a + b
end
"""

parser = get_parser_agent()
parse_tree = parser.parser.parse(code)
print("Parse tree:")
print(parse_tree.pretty())
print("\n" + "="*60)

ast = parser.parse(code)
print(f"AST type: {type(ast)}")
print(f"Num functions: {len(ast.functions)}")
if ast.functions:
    print(f"First function: {ast.functions[0]}")
else:
    print("No functions found!")
    print(f"AST: {ast}")
