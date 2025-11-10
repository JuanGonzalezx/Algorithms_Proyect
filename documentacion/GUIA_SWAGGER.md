# 🌐 GUÍA: Cómo Usar el Agente en Swagger UI

## 📋 Paso a Paso

### 1️⃣ Iniciar el Servidor

```bash
python main.py
```

Deberías ver algo como:
```
🚀 Iniciando Analizador de Complejidades Algorítmicas
📡 Servidor en 0.0.0.0:8000
✨ Aplicación iniciada correctamente
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 2️⃣ Abrir Swagger UI

Abre tu navegador y ve a:
```
http://localhost:8000/docs
```

### 3️⃣ Probar el Endpoint `/api/v1/health`

**¿Para qué sirve?** Verifica que el agente esté cargado y funcionando.

**En Swagger:**
1. Busca el endpoint `GET /api/v1/health`
2. Click en el endpoint para expandirlo
3. Click en **"Try it out"**
4. Click en **"Execute"**

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "service": "Analizador de Complejidad Algorítmica",
  "agents": {
    "syntax_validator": {
      "status": "available",
      "parser": "lark-lalr"
    }
  }
}
```

---

### 4️⃣ Validar Sintaxis con `/api/v1/validate-syntax`

**¿Para qué sirve?** Valida la sintaxis de tu pseudocódigo.

**En Swagger:**
1. Busca el endpoint `POST /api/v1/validate-syntax`
2. Click para expandirlo
3. Click en **"Try it out"**
4. En el campo "Request body", pega uno de estos ejemplos

---

## 📝 Ejemplos de Request Body

### ✅ Ejemplo 1: Código Válido Simple

```json
{
  "text": "x 🡨 5",
  "language_hint": "es"
}
```

**Respuesta esperada:**
```json
{
  "era_algoritmo_valido": true,
  "codigo_corregido": "x 🡨 5\n",
  "errores": [],
  "normalizaciones": [
    "Nueva línea añadida al final del archivo"
  ],
  "hints": {
    "parser_engine": "lark-lalr",
    "grammar_version": "1.0",
    "language_hint": "es",
    "total_errors": 0,
    "total_normalizations": 1,
    "code_length": 8,
    "line_count": 2
  }
}
```

---

### ✅ Ejemplo 2: Procedimiento Completo

```json
{
  "text": "procedimiento Suma(a, b)\nbegin\n    resultado 🡨 a + b\n    return resultado\nend",
  "language_hint": "es"
}
```

**Respuesta esperada:**
```json
{
  "era_algoritmo_valido": true,
  "codigo_corregido": "procedimiento Suma(a, b)\nbegin\n    resultado 🡨 a + b\n    return resultado\nend\n",
  "errores": [],
  "normalizaciones": [
    "Nueva línea añadida al final del archivo"
  ],
  "hints": {
    "parser_engine": "lark-lalr",
    "parse_tree_nodes": 21,
    "total_errors": 0
  }
}
```

---

### ✅ Ejemplo 3: Algoritmo de Ordenamiento (Burbuja)

```json
{
  "text": "procedimiento OrdenamientoBurbuja(A[1..n])\nbegin\n    i, j, temp\n    \n    for i 🡨 1 to n-1 do\n    begin\n        for j 🡨 1 to n-i do\n        begin\n            if A[j] > A[j+1] then\n            begin\n                temp 🡨 A[j]\n                A[j] 🡨 A[j+1]\n                A[j+1] 🡨 temp\n            end\n        end\n    end\nend",
  "language_hint": "es"
}
```

**Respuesta esperada:**
```json
{
  "era_algoritmo_valido": true,
  "codigo_corregido": "...",
  "errores": [],
  "normalizaciones": ["Nueva línea añadida al final del archivo"],
  "hints": {
    "parse_tree_nodes": 94,
    "line_count": 18
  }
}
```

---

### ❌ Ejemplo 4: Código con Errores

```json
{
  "text": "procedimiento Test(n)\nbegin\n    x 🡨 5\n    if x > 0 then\n    begin\n        x 🡨 x + 1\n    end",
  "language_hint": "es"
}
```

**Respuesta esperada (con errores):**
```json
{
  "era_algoritmo_valido": false,
  "codigo_corregido": "procedimiento Test(n)\nbegin\n    x 🡨 5\n    if x > 0 then\n    begin\n        x 🡨 x + 1\n    end\n",
  "errores": [
    {
      "linea": 8,
      "columna": 5,
      "regla": "Se esperaba: END, IF, FOR, WHILE, REPEAT, CALL, RETURN, NAME, ACCION, PROCEDIMIENTO",
      "detalle": "Unexpected token Token('$END', '') at line 8, column 5...",
      "sugerencia": "Token inesperado. Verifica que la sintaxis sea correcta."
    }
  ],
  "normalizaciones": [
    "Nueva línea añadida al final del archivo"
  ],
  "hints": {
    "total_errors": 1
  }
}
```

---

### ✅ Ejemplo 5: Código con Normalizaciones

```json
{
  "text": "procedimiento Comparar(x, y)\nbegin\n    if x <= y then\n    begin\n        mayor 🡨 y\n    end\n    if x >= y then\n    begin\n        mayor 🡨 x\n    end\nend",
  "language_hint": "es"
}
```

**Respuesta esperada:**
```json
{
  "era_algoritmo_valido": true,
  "codigo_corregido": "procedimiento Comparar(x, y)\nbegin\n    if x ≤ y then\n    begin\n        mayor 🡨 y\n    end\n    if x ≥ y then\n    begin\n        mayor 🡨 x\n    end\nend\n",
  "errores": [],
  "normalizaciones": [
    "Nueva línea añadida al final del archivo",
    "Operador '<=' normalizado a '≤'",
    "Operador '>=' normalizado a '≥'"
  ],
  "hints": {
    "total_normalizaciones": 3
  }
}
```

---

### ✅ Ejemplo 6: Búsqueda Binaria

```json
{
  "text": "procedimiento BusquedaBinaria(A[1..n], valor)\nbegin\n    inicio 🡨 1\n    fin 🡨 n\n    \n    while inicio <= fin do\n    begin\n        medio 🡨 └(inicio + fin) / 2┘\n        \n        if A[medio] = valor then\n        begin\n            return medio\n        end\n        else\n        begin\n            if A[medio] < valor then\n            begin\n                inicio 🡨 medio + 1\n            end\n            else\n            begin\n                fin 🡨 medio - 1\n            end\n        end\n    end\n    \n    return -1\nend",
  "language_hint": "es"
}
```

---

### ✅ Ejemplo 7: Factorial Recursivo

```json
{
  "text": "procedimiento Factorial(n)\nbegin\n    if n <= 1 then\n    begin\n        return 1\n    end\n    else\n    begin\n        return n * Factorial(n-1)\n    end\nend",
  "language_hint": "es"
}
```

---

## 🎨 Visualización en Swagger

Cuando ejecutes en Swagger, verás:

```
Request URL
http://localhost:8000/api/v1/validate-syntax

Response body (200)
{
  "era_algoritmo_valido": true,
  "codigo_corregido": "...",
  "errores": [],
  ...
}

Response headers
content-type: application/json; charset=utf-8
```

---

## 🔍 Campos del Response

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `era_algoritmo_valido` | boolean | `true` si la sintaxis es correcta |
| `codigo_corregido` | string | Código normalizado |
| `errores` | array | Lista de errores encontrados |
| `normalizaciones` | array | Normalizaciones aplicadas |
| `hints` | object | Metadatos adicionales |

### Estructura de `errores`:
```json
{
  "linea": 5,
  "columna": 10,
  "regla": "Se esperaba: END",
  "detalle": "Descripción completa del error",
  "sugerencia": "Cómo corregirlo"
}
```

### Estructura de `hints`:
```json
{
  "parser_engine": "lark-lalr",
  "grammar_version": "1.0",
  "language_hint": "es",
  "parse_tree_nodes": 94,
  "total_errors": 0,
  "total_normalizations": 2,
  "code_length": 316,
  "line_count": 17
}
```

---

## 💡 Tips para usar en Swagger

### 1. Usar saltos de línea
En JSON, usa `\n` para saltos de línea:
```json
{
  "text": "linea1\nlinea2\nlinea3"
}
```

### 2. Escapar caracteres especiales
Si usas comillas dentro del texto, escápalas:
```json
{
  "text": "comentario: \"esto es una prueba\""
}
```

### 3. Probar casos extremos
- Código vacío: `{"text": ""}`
- Solo espacios: `{"text": "   "}`
- Código muy largo: Pega un algoritmo completo

### 4. Ver respuestas de error
Swagger mostrará errores HTTP con detalles:
- **200**: Éxito (puede tener errores de sintaxis en el código)
- **422**: Validación fallida (JSON mal formado)
- **500**: Error interno del servidor

---

## 🚀 Workflow Recomendado

1. **Primero**: Probar con `GET /api/v1/health` → Verificar que el agente esté listo
2. **Segundo**: Probar con código simple → `x 🡨 5`
3. **Tercero**: Probar con procedimiento completo
4. **Cuarto**: Probar con código que tenga errores
5. **Quinto**: Probar con tu propio algoritmo

---

## 📸 Screenshots de Referencia

### Vista de Swagger UI:
```
┌─────────────────────────────────────────────────────┐
│ Analizador de Complejidades Algorítmicas           │
│ Version: 2.0.0                                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│ default                                             │
│                                                     │
│ ▼ GET /                                             │
│   Root                                              │
│                                                     │
│ agents                                              │
│                                                     │
│ ▼ GET  /api/v1/health                               │
│   Health Check                                      │
│                                                     │
│ ▼ POST /api/v1/validate-syntax                      │
│   Validar sintaxis de pseudocódigo                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🎓 Ejemplo Completo Paso a Paso

### Paso 1: Abrir Swagger
```
http://localhost:8000/docs
```

### Paso 2: Click en `POST /api/v1/validate-syntax`

### Paso 3: Click en "Try it out"

### Paso 4: Copiar y pegar este JSON:
```json
{
  "text": "procedimiento Suma(a, b)\nbegin\n    resultado 🡨 a + b\n    return resultado\nend",
  "language_hint": "es"
}
```

### Paso 5: Click en "Execute"

### Paso 6: Ver la respuesta:
```json
{
  "era_algoritmo_valido": true,
  "codigo_corregido": "procedimiento Suma(a, b)\nbegin\n    resultado 🡨 a + b\n    return resultado\nend\n",
  "errores": [],
  "normalizaciones": ["Nueva línea añadida al final del archivo"],
  "hints": {
    "parser_engine": "lark-lalr",
    "grammar_version": "1.0",
    "language_hint": "es",
    "parse_tree_nodes": 21,
    "total_errors": 0,
    "total_normalizations": 1,
    "code_length": 79,
    "line_count": 6
  }
}
```

---

## 🎯 ¡Listo para usar!

Ahora puedes:
- ✅ Validar cualquier pseudocódigo desde Swagger
- ✅ Ver errores detallados con línea y columna
- ✅ Obtener código normalizado
- ✅ Verificar que el agente funciona correctamente

---

## 📚 Documentación Adicional

- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/api/v1/health
