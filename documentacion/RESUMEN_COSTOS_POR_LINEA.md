# Resumen: Costos por Línea - Implementación Final

## ✅ Problema Resuelto

El endpoint `/api/v1/analyze` ahora retorna **TODAS** las líneas ejecutables en `per_line`, incluyendo:
- Sentencias de asignación (Assign)
- Condicionales (If)
- **Loops (For, While)** ← Ahora incluidos

## 📊 Formato de Salida

Cada línea muestra:
```
C_i * frecuencia_de_ejecución
```

Donde:
- **C_i**: Costo constante de la operación en la línea i
- **frecuencia_de_ejecución**: Expresión que indica cuántas veces se ejecuta

## 🔢 Ejemplos

### Bubble Sort

```python
Línea 7:  n ← length(A)
  Costo: 1                                    # Se ejecuta 1 vez

Línea 8:  for i ← 1 to n-1 do
  Costo: (n - 1 - 1 + 2) = n                  # Se evalúa n veces (n-1 entradas + 1 salida)

Línea 10: for j ← 1 to n-i do
  Costo: Sum((n - i - 1 + 2), (i, 1, n-1))    # Se evalúa Sum(n-i+1) veces

Línea 12: if (A[j] > A[j+1]) then
  Costo: Sum(Sum(1, (j, 1, n-i)), (i, 1, n-1)) # Se ejecuta en cada iteración de ambos loops

Línea 15-17: temp ← A[j], A[j] ← A[j+1], A[j+1] ← temp
  Costo: Sum(Sum(1, (j, 1, n-i)), (i, 1, n-1)) # Cada una se ejecuta en el cuerpo del if
```

## 🎯 Cálculo de Ejecuciones de For Loops

Para un `for var = start to end do`:
- **Número de ejecuciones de la línea del for**: `(end - start + 2)`
  - `end - start + 1` iteraciones que entran al body
  - `+1` iteración que sale (cuando `var > end`)

### Ejemplo: `for i = 1 to n-1 do`
- Iteraciones: i=1, i=2, ..., i=n-1 (n-1 valores)
- Salida: i=n (comprueba n ≤ n-1, falso, sale)
- **Total**: n evaluaciones de la condición

### Ejemplo: `for j = 1 to n-i do` (dentro del for de i)
- Por cada i: (n-i) - 1 + 2 = n-i+1 evaluaciones
- Para i=1: n evaluaciones
- Para i=2: n-1 evaluaciones
- ...
- Para i=n-1: 2 evaluaciones
- **Total**: Sum(n-i+1, i, 1, n-1)

## 🧮 Resolución de Sumatorias

El solver resuelve estas expresiones automáticamente:

```
Sum((n - i + 1), (i, 1, n-1))
  = Sum(n - i + 1, i, 1, n-1)
  = n*(n-1) - Sum(i, i, 1, n-1) + (n-1)
  = n*(n-1) - (n-1)*n/2 + (n-1)
  = (n-1)*(n - n/2 + 1)
  = (n-1)*(n+2)/2
```

## 📝 Cambios en el Código

### `app/shared/models.py`
- Agregado `LoopInfo` con campos: `var`, `start`, `end`
- Agregado `loop_info` a `NodeCost`

### `app/modules/analyzer/cost_model.py`
- `_analyze_for()`: Ahora guarda `LoopInfo` en cada nodo For
- `_generate_line_costs()`: 
  - Incluye **todos** los nodos con línea (no solo Assign/If)
  - Para For loops: calcula `(end - start + 2)` ejecuciones
  - Para otros nodos: multiplica por loops que los contienen
  - Usa `_wrap_in_sums()` para crear sumatorias anidadas

## ✅ Validación

Test exitoso con:
- ✅ Bubble Sort: 7 líneas (todas las ejecutables)
- ✅ Selection Sort: 9 líneas (todas las ejecutables)
- ✅ Solver resuelve correctamente todas las sumatorias
- ✅ Resultados: O(n²) para ambos algoritmos

## 🎉 Resultado Final

El endpoint ahora retorna:
```json
{
  "per_line": [
    {
      "line_number": 8,
      "code": "for i ← 1 to n-1 do",
      "operations": ["For"],
      "cost": {
        "best": "((n - 1) - 1 + 2)",
        "avg": "((n - 1) - 1 + 2)",
        "worst": "((n - 1) - 1 + 2)"
      }
    },
    // ... todas las demás líneas
  ]
}
```

¡Implementación completa! 🚀
