# 🚫 Restricciones del Parser AST Python → IR

Este documento describe las limitaciones actuales del parser AST para garantizar compatibilidad con el análisis de complejidad.

## ❌ Sintaxis NO Soportada

### 1. Tuple Unpacking en Asignaciones
```python
# ❌ NO FUNCIONA
a, b = b, a
x, y = obtener_coordenadas()
arr[i], arr[j] = arr[j], arr[i]

# ✅ USA EN SU LUGAR (variable temporal)
temp = a
a = b
b = temp

# ✅ O asignaciones individuales
resultado = obtener_coordenadas()
x = resultado[0]
y = resultado[1]
```

### 2. Asignaciones Múltiples
```python
# ❌ NO FUNCIONA
x = y = z = 0

# ✅ USA EN SU LUGAR
x = 0
y = 0
z = 0
```

### 3. Range con Step
```python
# ❌ NO FUNCIONA
for i in range(0, 10, 2):
    pass

# ✅ USA EN SU LUGAR
i = 0
while i < 10:
    # código aquí
    i += 2
```

### 4. Comparaciones Encadenadas
```python
# ❌ NO FUNCIONA
if a < b < c:
    pass

# ✅ USA EN SU LUGAR
if a < b and b < c:
    pass
```

### 5. For-else / While-else
```python
# ❌ NO FUNCIONA
for i in range(10):
    if encontrado:
        break
else:
    print("No encontrado")

# ✅ USA EN SU LUGAR
encontrado = False
for i in range(10):
    if condicion:
        encontrado = True
        break

if not encontrado:
    print("No encontrado")
```

### 6. Comprehensions
```python
# ❌ NO FUNCIONA
cuadrados = [x**2 for x in range(10)]
pares = {x for x in arr if x % 2 == 0}

# ✅ USA EN SU LUGAR
cuadrados = []
for x in range(10):
    cuadrados.append(x**2)

pares = []
for x in arr:
    if x % 2 == 0:
        pares.append(x)
```

### 7. Decoradores
```python
# ❌ NO FUNCIONA
@decorator
def funcion():
    pass

# ✅ Simplemente no uses decoradores
def funcion():
    pass
```

### 8. *args, **kwargs
```python
# ❌ NO FUNCIONA
def funcion(*args, **kwargs):
    pass

# ✅ USA parámetros explícitos
def funcion(param1, param2, param3):
    pass
```

### 9. Llamadas con Nombres Cualificados
```python
# ❌ NO FUNCIONA
resultado = math.sqrt(16)
objeto.metodo()

# ✅ USA llamadas simples
resultado = sqrt(16)  # Asume que sqrt está definido
```

### 10. Acceso a Arreglos Complejos
```python
# ❌ NO FUNCIONA
valor = matriz[i][j]
valor = obtener_array()[indice]

# ✅ USA acceso simple
fila = matriz[i]
valor = fila[j]

arr = obtener_array()
valor = arr[indice]
```

---

## ✅ Sintaxis Soportada

### Estructuras Básicas
```python
# Variables y literales
x = 5
nombre = "texto"
activo = True
vacio = None

# Asignaciones aumentadas
x += 1
y -= 2
z *= 3
```

### Estructuras de Control
```python
# If-else
if x > 0:
    print("positivo")
else:
    print("negativo")

# While
while i < n:
    i += 1

# For con range
for i in range(n):
    suma += i

for i in range(1, n):
    suma += arr[i]
```

### Operadores
```python
# Aritméticos
resultado = a + b - c * d / e
cociente = a // b  # división entera (mapea a "div")
resto = a % b      # módulo (mapea a "mod")

# Comparaciones
if x == y:
    pass
if x != y:
    pass
if x < y:
    pass
if x <= y:
    pass
if x > y:
    pass
if x >= y:
    pass

# Lógicos
if x > 0 and y < 10:
    pass
if a or b:
    pass
if not activo:
    pass

# Unarios
negativo = -x
opuesto = not True
```

### Funciones
```python
# Definición simple
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Con múltiples parámetros
def suma(a, b, c):
    return a + b + c

# Llamadas a funciones
resultado = factorial(5)
total = suma(1, 2, 3)
```

### Arreglos
```python
# Acceso simple
valor = arr[i]
arr[j] = nuevo_valor

# En expresiones
suma = arr[i] + arr[j]
if arr[0] < arr[n-1]:
    pass
```

---

## 📝 Ejemplo Completo: Selection Sort

### ❌ Versión NO Soportada
```python
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        # ❌ Tuple unpacking no soportado
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
```

### ✅ Versión Soportada
```python
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        # ✅ Usa variable temporal
        if min_idx != i:
            temp = arr[i]
            arr[i] = arr[min_idx]
            arr[min_idx] = temp
    return arr
```

---

## 🔧 Configuración de Gemini

El servicio `gemini_service.py` ahora incluye estas restricciones en el prompt para que Gemini genere código compatible automáticamente.

### Restricciones en el Prompt:
```python
RESTRICCIONES IMPORTANTES:
- NO uses tuple unpacking en asignaciones (NO: a, b = b, a)
- Para intercambiar valores, usa una variable temporal
- NO uses asignaciones múltiples (NO: x = y = z = 0)
- Usa asignaciones simples una por una
```

---

## 🧪 Tests

Todos estos casos están cubiertos en `tests/test_ast_builder.py`:
- ✅ `test_sum_array_with_for` - For loop básico
- ✅ `test_binary_search_with_while_if` - While + If anidados
- ✅ `test_factorial_recursive` - Recursión
- ✅ `test_unsupported_range_with_step` - Range con step (falla correctamente)
- ✅ `test_unsupported_chained_comparison` - Comparaciones encadenadas (falla)
- ✅ `test_invalid_python_syntax` - Sintaxis inválida (falla)
- ✅ `test_unsupported_tuple_unpacking` - Tuple unpacking (falla)

---

## 📊 Manejo de Errores

Cuando encuentras sintaxis no soportada, el endpoint `/api/v1/ast` responde:

```json
{
  "detail": "unsupported_syntax: Assignment target Tuple at line 10 not supported"
}
```

**Status Code**: `400 Bad Request`

Esto te indica exactamente qué reescribir en tu código Python.

---

## 🎯 Próximos Pasos (Futuras Mejoras)

Estas características podrían agregarse en versiones futuras:
- [ ] Soporte para tuple unpacking (descomposición en asignaciones temporales)
- [ ] Soporte para comprehensions (conversión a loops explícitos)
- [ ] Soporte para range con step (conversión a while)
- [ ] Soporte para comparaciones encadenadas (descomposición con and)
- [ ] Soporte para for-else/while-else (conversión con flags)

Por ahora, mantén el código simple y explícito para máxima compatibilidad. 🚀
