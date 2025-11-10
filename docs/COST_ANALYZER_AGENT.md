# Cost Analyzer Agent - Documentación

## Resumen

El **Cost Analyzer Agent** es el tercer agente del sistema de análisis de complejidad algorítmica. Su función es convertir el AST en **expresiones de costo simbólicas** (sumatorias) que representan la complejidad computacional del algoritmo.

## Arquitectura

```
Pseudocódigo → [syntax_validator] → Parse Tree
                                          ↓
                                    [parser] → AST
                                                ↓
                                    [cost_analyzer] → Sumatorias
```

## Características Principales

### 1. Análisis de Costos por Nodo

Cada nodo del AST recibe un análisis de costo considerando tres casos:
- **Mejor caso** (best): Escenario más favorable
- **Caso promedio** (avg): Comportamiento esperado
- **Peor caso** (worst): Escenario más desfavorable

### 2. Estrategia de Análisis

| Tipo de Nodo | Costo |
|-------------|-------|
| **Assign** | Constante: `1` |
| **Return** | Constante: `1` |
| **ExprStmt** | Constante: `1` |
| **For** | Sumatoria: `Sum(costo_body, (k, start, end))` |
| **While** | Mejor: `0`, Peor: `Sum(costo_body, (k, 1, n))` |
| **If** | Mejor: `min(then, else)`, Peor: `max(then, else)` |
| **Block** | Suma de costos de statements |

### 3. Sumatorias Anidadas

Los bucles anidados generan sumatorias anidadas:

```python
for i = 1 to n:
    for j = 1 to n:
        x = 1

# Costo: Sum(Sum(1, (k, 1, n)), (k, 1, n))
```

### 4. Notación de Sumatorias

Las sumatorias se representan como:
```
Sum(expresión, (variable, inicio, fin))
```

Ejemplos:
- `Sum(1, (k, 1, n))` → Σ(1) para k=1 hasta n → n iteraciones
- `Sum(Sum(1, (k, 1, n)), (k, 1, n))` → Doble sumatoria → n² iteraciones

## API Endpoint

### POST /api/v1/costs

Analiza el costo de un pseudocódigo completo (validación + parsing + análisis).

**Request:**
```json
{
  "text": "procedimiento test(n)\nbegin\n    for i 🡨 1 to n do\n    begin\n        x 🡨 1\n    end\nend",
  "language_hint": "es"
}
```

**Response (CostsOut):**
```json
{
  "per_node": [
    {
      "node_id": "Assign3",
      "node_type": "Assign",
      "cost": {
        "best": "1",
        "avg": "1",
        "worst": "1"
      }
    },
    {
      "node_id": "For2",
      "node_type": "For",
      "cost": {
        "best": "Sum(1, (k, 1, n))",
        "avg": "Sum(1, (k, 1, n))",
        "worst": "Sum(1, (k, 1, n))"
      }
    },
    {
      "node_id": "Prog1",
      "node_type": "Program",
      "cost": {
        "best": "Sum(1, (k, 1, n))",
        "avg": "Sum(1, (k, 1, n))",
        "worst": "Sum(1, (k, 1, n))"
      }
    }
  ],
  "total": {
    "best": "Sum(1, (k, 1, n))",
    "avg": "Sum(1, (k, 1, n))",
    "worst": "Sum(1, (k, 1, n))"
  }
}
```

## Uso Programático

### Ejemplo Básico

```python
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import get_cost_analyzer

code = """
procedimiento bubbleSort(A, n)
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

# Parsear a AST
parser = get_parser_agent()
ast = parser.parse(code)

# Analizar costos
analyzer = get_cost_analyzer()
costs = analyzer.analyze(ast)

print(f"Nodos analizados: {len(costs.per_node)}")
print(f"Costo total (peor caso): {costs.total.worst}")
# Output: Sum(Sum(max(1 + 1 + 1, 0), (k, 1, (n - i))), (k, 1, (n - 1)))
```

### Flujo Completo (3 Agentes)

```python
from app.modules.syntax_validator.agent import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import get_cost_analyzer
from app.shared.models import PseudocodeIn

code = "..."

# 1. Validar sintaxis
validator = get_syntax_validator()
validation = validator.validate(PseudocodeIn(text=code))

if validation.era_algoritmo_valido:
    # 2. Parsear a AST
    parser = get_parser_agent()
    ast = parser.parse(validation.codigo_corregido)
    
    # 3. Analizar costos
    analyzer = get_cost_analyzer()
    costs = analyzer.analyze(ast)
    
    print(costs.total.worst)
```

### Interfaz LangGraph

```python
# Usar como paso en un grafo de LangGraph
analyzer = get_cost_analyzer()
result = analyzer({"ast": ast_program})

if result["success"]:
    costs = result["costs"]
    print(f"Mejor caso: {costs.total.best}")
    print(f"Peor caso: {costs.total.worst}")
```

## Modelos de Datos

### CostExpr

```python
class CostExpr(BaseModel):
    best: str   # Costo en mejor caso
    avg: str    # Costo en caso promedio
    worst: str  # Costo en peor caso
```

### NodeCost

```python
class NodeCost(BaseModel):
    node_id: str      # ID único del nodo
    node_type: str    # Tipo: For, If, Assign, etc.
    cost: CostExpr    # Costos del nodo
```

### CostsOut

```python
class CostsOut(BaseModel):
    per_node: List[NodeCost]  # Costos individuales
    total: CostExpr           # Costo total del programa
```

## Ejemplos de Análisis

### Ejemplo 1: Bucle Simple

**Entrada:**
```
procedimiento suma(n)
begin
    s 🡨 0
    for i 🡨 1 to n do
    begin
        s 🡨 s + 1
    end
end
```

**Salida:**
```json
{
  "total": {
    "best": "1 + Sum(1, (k, 1, n))",
    "avg": "1 + Sum(1, (k, 1, n))",
    "worst": "1 + Sum(1, (k, 1, n))"
  }
}
```

**Interpretación:** O(n) - bucle con n iteraciones

### Ejemplo 2: Bucles Anidados

**Entrada:**
```
procedimiento bubbleSort(A, n)
begin
    for i 🡨 1 to n do
    begin
        for j 🡨 1 to n do
        begin
            temp 🡨 1
        end
    end
end
```

**Salida:**
```json
{
  "total": {
    "worst": "Sum(Sum(1, (k, 1, n)), (k, 1, n))"
  }
}
```

**Interpretación:** O(n²) - doble bucle anidado

### Ejemplo 3: Condicional

**Entrada:**
```
procedimiento buscar(arr, n, x)
begin
    if arr[1] = x then
    begin
        return 1
    end
    else
    begin
        for i 🡨 2 to n do
        begin
            if arr[i] = x then
            begin
                return i
            end
        end
    end
end
```

**Salida:**
```json
{
  "total": {
    "best": "min(1, ...)",
    "worst": "max(1, Sum(...))"
  }
}
```

**Interpretación:** Mejor caso O(1), peor caso O(n)

## Tests

Ejecutar tests del cost analyzer:

```bash
python test_cost_analyzer.py
```

**9 tests disponibles:**
1. ✅ Asignación simple (costo 1)
2. ✅ Bucle for (genera sumatoria)
3. ✅ Bucles anidados (sumatorias anidadas)
4. ✅ Condicionales if (mejor/peor caso)
5. ✅ Bucle while (mejor caso 0)
6. ✅ Programa completo
7. ✅ Serialización a JSON
8. ✅ Interfaz LangGraph
9. ✅ Múltiples funciones

## Limitaciones Actuales

1. **While loops:** Se asume n iteraciones en peor caso (heurística conservadora)
2. **Recursión:** No se detecta ni se analiza actualmente
3. **Llamadas a funciones:** Se cuentan como costo 1
4. **Simplificación:** Las sumatorias no se simplifican automáticamente

## Próximos Pasos

El siguiente agente podría:

1. **Simplificador de Sumatorias**: Reducir `Sum(1, (k, 1, n))` a `n`
2. **Detector de Complejidad**: Convertir sumatorias a notación Big-O
3. **Analizador de Recursión**: Detectar y analizar funciones recursivas
4. **Optimizador**: Sugerir mejoras algorítmicas

## Health Check

El endpoint `/api/v1/health` ahora incluye el cost_analyzer:

```json
{
  "status": "healthy",
  "agents": {
    "syntax_validator": {"status": "available"},
    "parser": {"status": "available"},
    "cost_analyzer": {
      "status": "available",
      "analyzer": "summation-based"
    }
  }
}
```

## Archivos Creados

- `app/modules/analyzer/__init__.py`: Módulo Python
- `app/modules/analyzer/cost_model.py`: CostAnalyzer y CostAnalyzerAgent (420 líneas)
- `app/shared/models.py`: Modelos CostExpr, NodeCost, CostsOut agregados
- `app/api/routes.py`: Endpoint POST /api/v1/costs agregado
- `test_cost_analyzer.py`: 9 tests completos
- `ejemplo_cost_analyzer.py`: 6 ejemplos de uso

---

**Implementado por:** GitHub Copilot  
**Fecha:** Noviembre 2025  
**Versión:** 1.0  
**Estado:** ✅ Completo y probado (9/9 tests passing)
