# Fix: Costos por Línea con Probabilidades Condicionales

## Problema Identificado

En la salida del API para "bublesort", los costos por línea (`per_line`) mostraban valores idénticos para los casos best/avg/worst en todas las líneas, incluso para las líneas dentro de bloques condicionales (if/else).

**Ejemplo del problema:**
```json
"line_number": 9,
"code": "temp 🡨 A[j]",
"cost": {
    "best": "Sum(Sum(1, (j, 1, (n-i))), (i, 1, (n-1)))",
    "avg": "Sum(Sum(1, (j, 1, (n-i))), (i, 1, (n-1)))",  // ❌ Debería ser diferente
    "worst": "Sum(Sum(1, (j, 1, (n-i))), (i, 1, (n-1)))"
}
```

## Causa Raíz

La función `_generate_line_costs()` en `app/modules/analyzer/cost_model.py`:
- ✅ Rastreaba correctamente los bucles (For/While) que contenían cada línea
- ❌ **NO** rastreaba los condicionales (If/else) que contenían cada línea
- ❌ **NO** aplicaba probabilidades condicionales según el caso (best/avg/worst)

## Solución Implementada

### 1. Rastrear Bloques Condicionales

Se agregó código para detectar qué líneas están dentro de bloques `If`:

```python
# Encontrar todos los If nodes
if_nodes = [node for node in self.costs 
           if node.node_type == "If" and node.line_start and node.line_end]

# Ordenar por rango (los más externos primero)
if_nodes.sort(key=lambda n: (n.line_start, -n.line_end))

# Crear un mapa: line_number -> número de ifs que la contienen
line_to_if_depth = {}
for line_num in range(1, len(lines) + 1):
    if_depth = 0
    for if_node in if_nodes:
        # Verificar si esta línea está DENTRO del if
        if if_node.line_start < line_num <= if_node.line_end:
            if_depth += 1
    if if_depth > 0:
        line_to_if_depth[line_num] = if_depth
```

### 2. Aplicar Probabilidades Según el Caso

Se modificó la sección de cálculo de costos para aplicar probabilidades condicionales:

```python
# Si está dentro de condicionales, aplicar probabilidades
if if_depth > 0:
    # Best case: el if casi nunca entra (probabilidad muy baja)
    # Para simplificar, usamos 0 (el if nunca entra en el mejor caso)
    base_cost_best = "0"
    
    # Average case: el if entra ~50% de las veces
    # Multiplicamos por 0.5^if_depth
    probability = 0.5 ** if_depth
    if base_cost_avg != "0":
        base_cost_avg = f"({probability} * ({base_cost_avg}))"
    
    # Worst case: el if siempre entra (probabilidad = 1.0)
    # No cambia el costo
```

## Resultado

Ahora los costos por línea reflejan correctamente las probabilidades condicionales:

### Líneas Fuera del If
```json
{
    "line_number": 7,
    "code": "if (A[j] > A[j+1]) then",
    "cost": {
        "best": "Sum(Sum(1, (j, 1, (n-i))), (i, 1, (n-1)))",
        "avg": "Sum(Sum(1, (j, 1, (n-i))), (i, 1, (n-1)))",
        "worst": "Sum(Sum(1, (j, 1, (n-i))), (i, 1, (n-1)))"
    }
}
```
✅ La evaluación de la condición se ejecuta siempre (mismo costo en todos los casos)

### Líneas Dentro del If
```json
{
    "line_number": 9,
    "code": "temp 🡨 A[j]",
    "cost": {
        "best": "0",                                              // ✅ Nunca se ejecuta
        "avg": "Sum(Sum((0.5 * (1)), (j, 1, (n-i))), ...)",     // ✅ 50% probabilidad
        "worst": "Sum(Sum(1, (j, 1, (n-i))), (i, 1, (n-1)))"    // ✅ Siempre se ejecuta
    }
}
```

### Costos Totales
```json
{
    "best": "Sum(Sum(1, (j, 1, (n-i))), (i, 1, (n-1)))",
    "avg": "Sum(Sum(1 + 0.5*(1 + 1 + 1), (j, 1, (n-i))), (i, 1, (n-1)))",
    "worst": "Sum(Sum(1 + max(1 + 1 + 1, 0), (j, 1, (n-i))), (i, 1, (n-1)))"
}
```

## Interpretación de los Casos

### Best Case (Mejor Caso)
- **Lista ya ordenada**: El condicional `A[j] > A[j+1]` nunca se cumple
- **Líneas dentro del if**: Costo = `0`
- **Total**: Solo se cuentan las evaluaciones de la condición

### Average Case (Caso Promedio)
- **Lista parcialmente desordenada**: El condicional se cumple ~50% de las veces
- **Líneas dentro del if**: Costo = `0.5 * costo_base`
- **Total**: Evaluaciones + mitad de los intercambios

### Worst Case (Peor Caso)
- **Lista ordenada inversamente**: El condicional siempre se cumple
- **Líneas dentro del if**: Costo = `costo_base` completo
- **Total**: Evaluaciones + todos los intercambios

## Archivos Modificados

1. **app/modules/analyzer/cost_model.py**
   - Función `_generate_line_costs()` (líneas 668-800)
   - Se agregó rastreo de nodos If
   - Se agregó aplicación de probabilidades condicionales

## Tests de Verificación

1. **test_if_costs.py**: Test básico con pseudocódigo simple
2. **test_analysis_summary.py**: Análisis detallado de los costos
3. **test_bublesort_natural.py**: Test con lenguaje natural "bublesort"

Todos los tests pasan exitosamente ✅

## Impacto

- ✅ Los costos por línea ahora son precisos y diferenciados por caso
- ✅ Los métodos de solución (bloques y línea por línea) ahora usan datos correctos
- ✅ El análisis de complejidad es más preciso y educativo
- ✅ Compatible con ifs anidados (usa `if_depth` para múltiples niveles)

## Nota Importante

Esta implementación usa una probabilidad fija de 0.5 (50%) para el caso promedio. En un análisis más sofisticado, esta probabilidad podría:
- Ser configurable por el usuario
- Depender del tipo de algoritmo
- Calcularse a partir de propiedades del input

Por ahora, 0.5 es un valor razonable y ampliamente usado en análisis de complejidad estándar.
