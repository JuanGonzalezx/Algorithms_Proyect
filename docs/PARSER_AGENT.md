# Agente Parser - Documentación

## Resumen

El **Parser Agent** es el segundo agente del sistema de análisis de complejidad algorítmica. Su función es transformar el parse tree de Lark (generado por el `syntax_validator`) en un **AST (Abstract Syntax Tree) custom** con tipos fuertemente tipados.

## Arquitectura

```
Pseudocódigo → [syntax_validator] → Lark Parse Tree
                                             ↓
                                    [parser] → AST Custom
```

## Características Principales

### 1. Transformación Lark → AST

Utiliza un `Transformer` de Lark que convierte cada nodo del parse tree en objetos Python tipados:

- **Program**: Raíz del AST, contiene lista de funciones
- **Function**: Procedimiento con nombre, parámetros y body
- **Statements**: For, While, If, Assign, Return, ExprStmt
- **Expressions**: BinOp, UnOp, Compare, Call, Var, Literal, ArrayAccess

### 2. Gramática Compartida

Reutiliza la misma gramática (`app/shared/grammar/grammar.lark`) que el `syntax_validator`, garantizando consistencia.

### 3. Serialización JSON

El AST generado es completamente serializable a JSON gracias al método `to_dict()` de cada nodo.

### 4. Interfaz LangGraph

Compatible con LangGraph mediante el método `__call__()`:

```python
result = parser_agent({"pseudocode": code})
# result = {"ast": Program(...), "success": True, "error": None}
```

## Sintaxis del Pseudocódigo

**IMPORTANTE**: La gramática usa keywords en inglés con algunas palabras en español:

### Procedimientos
```
procedimiento NombreFuncion(param1, param2)
begin
    statement1
    statement2
end
```

### Bucles FOR
```
for i 🡨 1 to n do
begin
    statement
end
```

### Bucles WHILE
```
while condicion do
begin
    statement
end
```

### Condicionales IF
```
if condicion then
begin
    statement
end
else
begin
    statement
end
```

### Asignaciones
```
variable 🡨 expresion
arr[i] 🡨 valor
```

### Expresiones
- Aritméticas: `+`, `-`, `*`, `/`, `div`, `mod`
- Comparación: `=`, `≠`, `<`, `>`, `≤`, `≥`
- Lógicas: `and`, `or`, `not`

## API Endpoint

### POST /api/v1/parse

Convierte pseudocódigo a AST.

**Request:**
```json
{
  "text": "procedimiento suma(a, b)\nbegin\n    return a + b\nend",
  "language_hint": "es"
}
```

**Response:**
```json
{
  "success": true,
  "ast": {
    "type": "Program",
    "functions": [
      {
        "type": "Function",
        "name": "suma",
        "params": [
          {"name": "a"},
          {"name": "b"}
        ],
        "body": {
          "type": "Block",
          "statements": [
            {
              "type": "Return",
              "value": {
                "type": "BinOp",
                "op": "+",
                "left": {"type": "Var", "name": "a"},
                "right": {"type": "Var", "name": "b"}
              }
            }
          ]
        }
      }
    ]
  },
  "metadata": {
    "num_functions": 1,
    "num_nodes": 15,
    "function_names": ["suma"]
  },
  "error": null
}
```

## Uso Programático

### Ejemplo Básico

```python
from app.modules.parser.service import get_parser_agent

code = """
procedimiento ordenamientoBurbuja(A, n)
begin
    for i 🡨 1 to n - 1 do
    begin
        for j 🡨 1 to n - i do
        begin
            if A[j] > A[j + 1] then
            begin
                temp 🡨 A[j]
                A[j] 🡨 A[j + 1]
                A[j + 1] 🡨 temp
            end
        end
    end
end
"""

parser = get_parser_agent()
ast = parser.parse(code)

print(f"Funciones: {len(ast.functions)}")
print(f"Nombre: {ast.functions[0].name}")
print(f"Parámetros: {[p.name for p in ast.functions[0].params]}")
```

### Serialización

```python
# Convertir AST a diccionario
ast_dict = ast.to_dict()

# Convertir a JSON
import json
json_str = json.dumps(ast_dict, indent=2, ensure_ascii=False)
```

### Interfaz LangGraph

```python
result = parser({"pseudocode": code})

if result["success"]:
    ast = result["ast"]
    print(f"✓ Parseado exitosamente: {len(ast.functions)} funciones")
else:
    print(f"✗ Error: {result['error']}")
```

## Tests

Ejecutar tests del parser:

```bash
python test_parser.py
```

**9 tests disponibles:**
1. ✅ Procedimiento simple
2. ✅ Bucle for con arrays
3. ✅ Bubble sort completo
4. ✅ Bucle while
5. ✅ Condicionales anidados
6. ✅ Serialización AST
7. ✅ Operadores de comparación
8. ✅ Interfaz LangGraph
9. ✅ Manejo de errores

## Diferencias con Syntax Validator

| Aspecto | Syntax Validator | Parser |
|---------|-----------------|---------|
| **Salida** | Parse tree de Lark (~99 nodos) | AST custom (~30-40 nodos) |
| **Propósito** | Validar sintaxis | Preparar para análisis |
| **Nodos** | Tokens + reglas gramática | Solo nodos semánticos |
| **Tipos** | Tree de Lark | Clases Python tipadas |
| **Serializable** | No directamente | Sí (to_dict()) |

## Próximos Pasos

El AST generado por este agente será consumido por:

1. **Agente de Análisis de Complejidad**: Calculará O(n) usando visitors
2. **Agente de Optimización**: Sugerirá mejoras algorítmicas
3. **Agente de Documentación**: Generará explicaciones del código

## Archivos Creados

- `app/modules/parser/__init__.py`: Módulo Python
- `app/modules/parser/service.py`: ParserAgent y PseudocodeToASTTransformer (370 líneas)
- `app/shared/models.py`: Modelos ASTResult, ASTNode agregados
- `app/api/routes.py`: Endpoint POST /api/v1/parse agregado
- `test_parser.py`: 9 tests completos
- `debug_parser.py`: Script de debugging

## Health Check

El endpoint `/api/v1/health` ahora incluye el parser agent:

```json
{
  "status": "healthy",
  "agents": {
    "syntax_validator": {
      "status": "available",
      "parser": "lark-lalr"
    },
    "parser": {
      "status": "available",
      "transformer": "custom-ast"
    }
  }
}
```

## Ejemplo de AST para Bubble Sort

```json
{
  "type": "Program",
  "functions": [
    {
      "type": "Function",
      "name": "ordenamientoBurbuja",
      "params": [{"name": "A"}, {"name": "n"}],
      "body": {
        "type": "Block",
        "statements": [
          {
            "type": "For",
            "var": "i",
            "start": {"type": "Literal", "value": 1},
            "end": {
              "type": "BinOp",
              "op": "-",
              "left": {"type": "Var", "name": "n"},
              "right": {"type": "Literal", "value": 1}
            },
            "body": { ... }
          }
        ]
      }
    }
  ]
}
```

---

**Implementado por:** GitHub Copilot  
**Fecha:** 2025  
**Versión:** 1.0  
**Estado:** ✅ Completo y probado
