# 🤖 Generador de Código con IA - Analizador Algorítmico

Sistema inteligente que utiliza **Google Gemini AI** para convertir descripciones en lenguaje natural a pseudocódigo estructurado y código Python implementable. Desarrollado con FastAPI y enfocado en análisis y generación automática de algoritmos.

## 🎯 Objetivo

Proveer una API REST que permita:
- ✅ Convertir descripciones en lenguaje natural a **pseudocódigo normalizado**
- ✅ Generar **código Python** ejecutable a partir de descripciones
- ✅ Guardar automáticamente los algoritmos generados
- 🔄 *Próximamente*: Análisis automático de complejidad computacional

## 🚀 Tecnologías

- **Backend**: FastAPI 0.104+
- **IA/LLM**: Google Gemini 2.5 Pro API
- **Parser**: Lark (gramática formal para pseudocódigo)
- **Validación**: Pydantic 2.5+
- **Python**: 3.10+
- **Config**: python-decouple (.env)

## 📁 Estructura del Proyecto

```
Algorithms_Proyect/
├── main.py                           # 🚀 Punto de entrada de la API FastAPI
├── requirements.txt                  # 📦 Dependencias del proyecto
├── .env                             # 🔐 Variables de entorno (GEMINI_API_KEY)
├── app/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py              # ⚙️ Configuración centralizada
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── analyzer_controller.py   # 🎮 Endpoints de la API
│   ├── core/
│   │   ├── __init__.py
│   │   ├── py_ast_builder.py        # 🐍 Parser Python → IR
│   │   └── psc_parser.py            # 📝 Parser Pseudocódigo → IR
│   ├── grammar/
│   │   └── pseudocode.lark          # 📝 Gramática formal EBNF
│   ├── models/
│   │   ├── ast_nodes.py             # 🌳 Nodos del AST/IR (dataclasses)
│   │   └── schemas.py               # 📋 Modelos Pydantic (API)
│   └── services/
│       ├── __init__.py
│       ├── gemini_service.py        # 🤖 Integración con Gemini AI
│       └── ast_service.py           # 🌳 Servicio de construcción AST
├── tests/
│   ├── test_ast_builder.py          # ✅ Tests parser Python (7 tests)
│   └── test_psc_parser.py           # ✅ Tests parser Pseudocódigo (8 tests)
├── docs/
│   ├── PARSER_PSEUDOCODIGO.md       # 📖 Documentación parser PSC
│   ├── RESTRICCIONES_AST.md         # 📖 Restricciones Python
│   ├── IMPLEMENTACION_AST.md        # 📖 Detalles implementación
│   └── ejemplos/
│       ├── ejemplos_prueba.md       # 📖 Ejemplos de uso
│       └── algoritmos_guardados/    # 💾 Códigos generados (auto-creado)
└── test_*.py                        # 🧪 Scripts de prueba manual
```

## 🔧 Instalación

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/JuanGonzalezx/Algorithms_Proyect.git
cd Algorithms_Proyect
```

### 2️⃣ Crear y activar entorno virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar variables de entorno
Crear archivo `.env` en la raíz del proyecto:
```env
# API Keys
GEMINI_API_KEY=tu_api_key_de_google_gemini_aqui

# Server configuration (opcional)
HOST=localhost
PORT=8000
DEBUG=True

# Model configuration (opcional)
MAX_INPUT_LENGTH=10000
TIMEOUT_SECONDS=30
```

**⚠️ Importante**: Obtén tu API key de Gemini en: https://makersuite.google.com/app/apikey

## ▶️ Ejecución

```bash
python main.py
```

El servidor estará disponible en: **http://localhost:8000**

### Logs esperados:
```
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
INFO:     🚀 Iniciando Analizador de Complejidades Algorítmicas
INFO:     📡 Servidor configurado en localhost:8000
INFO:     🔧 Modo debug: True
INFO:     ✅ API de Gemini configurada correctamente
INFO:     Application startup complete.
```

## 🌐 API Endpoints

### 📋 Documentación Interactiva
- **Swagger UI**: http://localhost:8000/docs 👈 *Interfaz para probar los endpoints*
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 🔍 Endpoints Disponibles

| Endpoint | Método | Descripción | Request Body |
|----------|--------|-------------|--------------|
| `/api/v1/health` | GET | ✅ Verificación de salud del servicio | - |
| `/api/v1/normalize` | POST | 📝 Convierte lenguaje natural a pseudocódigo | `InputRequest` |
| `/api/v1/generate-code` | POST | 🐍 Genera código Python (sin guardar) | `InputRequest` |
| `/api/v1/generate` | POST | 💾 Genera código Python y lo guarda | `GenerateRequest` |
| `/api/v1/ast` | POST | 🌳 **Construye AST/IR desde Python o pseudocódigo** | `ASTRequest` |

---

### 📝 Ejemplos Detallados

#### 1. Health Check
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```
**Respuesta:**
```json
{
  "status": "healthy",
  "service": "Analizador de Complejidades",
  "version": "1.0.0"
}
```

---

#### 2. Normalizar a Pseudocódigo
**Descripción**: Convierte lenguaje natural a pseudocódigo estructurado.

```bash
curl -X POST "http://localhost:8000/api/v1/normalize" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Algoritmo que sume todos los números de un arreglo usando un ciclo for"
  }'
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/normalize",
    json={
        "content": "Algoritmo que sume todos los números de un arreglo usando un ciclo for"
    }
)
print(response.json()["normalized_pseudocode"])
```

**Respuesta:**
```json
{
  "original_content": "Algoritmo que sume todos los números...",
  "normalized_pseudocode": "sumar_arreglo(A, n) begin\n  suma 🡨 0\n  for i 🡨 1 to n do begin\n    suma 🡨 suma + A[i]\n  end\n  return suma\nend",
  "input_type_detected": "natural_language",
  "is_valid_pseudocode": true,
  "correction_applied": true
}
```

---

#### 3. Generar Código Python (sin guardar)
**Descripción**: Genera código Python implementable sin guardarlo en archivo.

```bash
curl -X POST "http://localhost:8000/api/v1/generate-code" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Implementa el algoritmo de búsqueda binaria"
  }'
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/generate-code",
    json={
        "content": "Implementa el algoritmo de búsqueda binaria"
    }
)
print(response.json()["generated_code"])
```

**Respuesta:**
```json
{
  "description": "Implementa el algoritmo de búsqueda binaria",
  "generated_code": "def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    ...",
  "language": "python"
}
```

---

#### 4. Generar y Guardar Código
**Descripción**: Genera código Python y lo guarda en `docs/ejemplos/algoritmos_guardados/`.

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Función recursiva para calcular Fibonacci",
    "filename": "fibonacci.py"
  }'
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/generate",
    json={
        "description": "Función recursiva para calcular Fibonacci",
        "filename": "fibonacci.py"
    }
)
print(f"Guardado en: {response.json()['saved_path']}")
```

**Respuesta:**
```json
{
  "saved_path": "C:\\...\\docs\\ejemplos\\algoritmos_guardados\\fibonacci.py",
  "code": "# Prompt:\n# Función recursiva para calcular Fibonacci\n\ndef fibonacci(n):\n    ..."
}
```

---

#### 5. 🌳 Construcción de AST (Python o Pseudocódigo) **[ACTUALIZADO]**
**Descripción**: Parsea código fuente (Python o pseudocódigo) y genera un AST normalizado en formato JSON (Representación Intermedia unificada).

**🆕 Características del Parser de Pseudocódigo:**
- ✅ **Sintaxis flexible**: Soporta `procedimiento` o directamente `NombreFuncion(params)`
- ✅ **Declaraciones de variables**: `i, j, min_index, temp` (ignoradas en AST)
- ✅ **Comentarios**: `► Este es un comentario` (ignorados en parsing)
- ✅ **Asignaciones a arrays**: `A[i] 🡨 valor` o `A[i][j] 🡨 valor`
- ✅ **Paréntesis en condiciones**: `if (A[j] < A[min_index]) then`
- ✅ **Bloques begin...end**: Múltiples statements correctamente agrupados
- ✅ **IR unificada**: Python y pseudocódigo generan la misma estructura

**Desde Python:**
```bash
curl -X POST "http://localhost:8000/api/v1/ast" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "def suma(a, b):\n    return a + b",
    "from_lang": "python"
  }'
```

**Desde Pseudocódigo (con "procedimiento"):**
```bash
curl -X POST "http://localhost:8000/api/v1/ast" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "procedimiento suma(a, b)\nbegin\n    return a + b\nend",
    "from_lang": "pseudocode"
  }'
```

**Desde Pseudocódigo (sin "procedimiento"):**
```bash
curl -X POST "http://localhost:8000/api/v1/ast" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "SelectionSort(A)\nbegin\n    n 🡨 length(A)\n    for i 🡨 1 to n-1 do\n    begin\n        ► Código aquí\n    end\nend",
    "from_lang": "pseudocode"
  }'
```

**Python:**
```python
import requests

# Ejemplo 1: Parsear Python
response = requests.post(
    "http://localhost:8000/api/v1/ast",
    json={
        "content": """
def binary_search(arr, target, n):
    left = 0
    right = n - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
        """,
        "from_lang": "python"
    }
)
print(response.json())

# Ejemplo 2: Parsear pseudocódigo (normalizado por Gemini)
response_psc = requests.post(
    "http://localhost:8000/api/v1/ast",
    json={
        "content": """
SelectionSort(A)
begin
    n 🡨 length(A)
    i, j, min_index, temp

    ► Recorre el arreglo
    for i 🡨 1 to n - 1 do
    begin
        min_index 🡨 i
        
        for j 🡨 i + 1 to n do
        begin
            if (A[j] < A[min_index]) then
            begin
                min_index 🡨 j
            end
        end
        
        ► Intercambia elementos
        if (min_index ≠ i) then
        begin
            temp 🡨 A[i]
            A[i] 🡨 A[min_index]
            A[min_index] 🡨 temp
        end
    end
end
        """,
        "from_lang": "pseudocode"
    }
)
print(response_psc.json())
```

**Respuesta (Python y pseudocódigo generan la misma estructura IR):**
```json
{
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
}
```

**⚠️ Restricciones del parser Python:**
- ❌ No soporta tuple unpacking: `a, b = b, a`
- ❌ No soporta asignación múltiple: `a = b = 0`
- ❌ No soporta `range()` con step: `range(0, 10, 2)`
- ❌ No soporta comparaciones encadenadas: `0 < x < 10`

Ver [`RESTRICCIONES_AST.md`](RESTRICCIONES_AST.md) para detalles completos.

**📖 Documentación adicional:**
- Parser de pseudocódigo: [`PARSER_PSEUDOCODIGO.md`](PARSER_PSEUDOCODIGO.md)
- Implementación AST: [`IMPLEMENTACION_AST.md`](IMPLEMENTACION_AST.md)

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/generate",
    json={
        "description": "Función recursiva para calcular Fibonacci",
        "filename": "fibonacci.py"
    }
)
print(f"Guardado en: {response.json()['saved_path']}")
```

**Respuesta:**
```json
{
  "saved_path": "C:\\...\\docs\\ejemplos\\algoritmos_guardados\\fibonacci.py",
  "code": "# Prompt:\n# Función recursiva para calcular Fibonacci\n\ndef fibonacci(n):\n    ..."
}
```

## 🔄 Flujo del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    Usuario envía descripción                     │
│         (Lenguaje natural, pseudocódigo o código Python)         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API FastAPI (main.py)                         │
│                  Recibe request en endpoint                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Analyzer Controller (controllers/)                  │
│              - /normalize → Convertir a pseudocódigo             │
│              - /generate-code → Generar Python                   │
│              - /generate → Generar y guardar                     │
│              - /ast → Construir AST/IR (NUEVO)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
          ┌──────────────────┐  ┌─────────────────┐
          │ Gemini Service   │  │  AST Service    │
          │ (services/)      │  │  (services/)    │
          │                  │  │                 │
          │ - normalize()    │  │ - Python → IR   │
          │ - generate()     │  │ - Pseudocode→IR │
          └────────┬─────────┘  └────────┬────────┘
                   │                     │
                   ▼                     ▼
          ┌──────────────────┐  ┌─────────────────┐
          │ Google Gemini AI │  │  Lark Parser    │
          │     (2.5 Pro)    │  │  + Transformer  │
          └────────┬─────────┘  └────────┬────────┘
                   │                     │
                   └──────────┬──────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Respuesta al usuario (JSON)                         │
│      - Pseudocódigo estructurado (con 🡨 para asignaciones)       │
│      - Código Python ejecutable                                  │
│      - Archivo guardado (opcional)                               │
│      - AST/IR unificada en JSON (NUEVO)                          │
└─────────────────────────────────────────────────────────────────┘
```

### Flujo de Parsing AST

```
┌────────────────┐
│ Código fuente  │
│ (Python o PSC) │
└───────┬────────┘
        │
        ▼
┌────────────────────────┐
│  AST Service           │
│  - Detecta lenguaje    │
│  - Selecciona parser   │
└───────┬────────────────┘
        │
   ┌────┴────┐
   ▼         ▼
┌──────┐  ┌──────────┐
│Python│  │Pseudocode│
│Parser│  │  Parser  │
└──┬───┘  └────┬─────┘
   │           │
   │  ┌────────┴───────────────────┐
   │  │ Lark Grammar               │
   │  │ - Procedimientos           │
   │  │ - Declaraciones variables  │
   │  │ - Asignaciones (lvalue)    │
   │  │ - Estructuras de control   │
   │  │ - Comentarios (ignorados)  │
   │  └────────┬───────────────────┘
   │           │
   │           ▼
   │  ┌───────────────────┐
   │  │ PseudocodeToIR    │
   │  │ (Transformer)     │
   │  │ - then_part()     │
   │  │ - else_part()     │
   │  │ - lvalue()        │
   │  │ - var_declaration │
   │  └────────┬──────────┘
   │           │
   └───────┬───┘
           ▼
┌──────────────────────┐
│  Representación      │
│  Intermedia (IR)     │
│  - Program           │
│  - Function          │
│  - Block, Stmt       │
│  - Expr (BinOp, etc) │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  JSON Response       │
│  (Unified AST)       │
└──────────────────────┘
```

## 📖 Gramática de Pseudocódigo Soportada

El sistema genera pseudocódigo siguiendo estas reglas formales (ver [`PARSER_PSEUDOCODIGO.md`](docs/PARSER_PSEUDOCODIGO.md) para detalles completos).

### Estructuras Básicas:

| Estructura | Sintaxis | Ejemplo |
|------------|----------|---------|
| **Procedimiento** | `procedimiento nombre(params) begin ... end` o `nombre(params) begin ... end` | `factorial(n) begin ... end` |
| **Asignación** | `variable 🡨 valor` | `suma 🡨 0` |
| **Asignación Array** | `array[indice] 🡨 valor` | `A[i] 🡨 10` |
| **Declaración vars** | `var1, var2, var3` | `i, j, temp` |
| **For Loop** | `for var 🡨 inicio to fin do begin ... end` | `for i 🡨 1 to n do begin ... end` |
| **While Loop** | `while condicion do begin ... end` | `while (i < n) do begin ... end` |
| **Repeat Until** | `repeat begin ... end until condicion` | `repeat begin ... end until (suma > 100)` |
| **Condicional** | `if condicion then begin ... end [else begin ... end]` | `if (x > 0) then begin ... end` |
| **Llamada** | `CALL funcion(params)` o `funcion(params)` | `CALL ordenar(A, n)` |
| **Arreglos** | `A[i]` o `A[i][j]` (multi-dimensional) | `A[1]`, `matriz[i][j]` |
| **Comentario** | `► texto` | `► Este es un comentario` |
| **Booleanos** | `T`, `F` | `esPar 🡨 T` |

### Operadores:
- **Aritméticos**: `+`, `-`, `*`, `/`, `mod`, `div`
- **Lógicos**: `and`, `or`, `not`
- **Relacionales**: `<`, `>`, `≤`, `>=`, `=`, `≠`, `!=`, `==`

### 🆕 Características del Parser:

#### ✅ Sintaxis Flexible
```pseudocode
# Con palabra clave "procedimiento"
procedimiento buscar(A, n)
begin
    ...
end

# Sin palabra clave (compatible con output de normalize)
buscar(A, n)
begin
    ...
end
```

#### ✅ Declaraciones de Variables
```pseudocode
procedimiento ejemplo()
begin
    i, j, k, temp    ► Declaración (ignorada en AST)
    suma 🡨 0         ► Asignación real
end
```

#### ✅ Asignaciones a Arrays
```pseudocode
# Arrays unidimensionales
A[i] 🡨 valor
temp 🡨 A[j]

# Arrays multidimensionales
matriz[i][j] 🡨 0
valor 🡨 matriz[x][y]
```

#### ✅ Paréntesis Opcionales en Condiciones
```pseudocode
# Con paréntesis (más legible)
if (A[j] < A[min_index]) then
begin
    min_index 🡨 j
end

# Sin paréntesis (también válido)
if A[j] < A[min_index] then
begin
    min_index 🡨 j
end
```

#### ✅ Comentarios Ignorados
```pseudocode
procedimiento ejemplo()
begin
    ► Este comentario se ignora en el parsing
    suma 🡨 0
    ► Los comentarios no aparecen en el AST
end
```

### Ejemplo Completo:
```
busqueda_binaria(A, n, objetivo) begin
  ► Búsqueda binaria en arreglo ordenado
  izq 🡨 1
  der 🡨 n
  
  while (izq ≤ der) do begin
    medio 🡨 (izq + der) div 2
    
    if (A[medio] = objetivo) then begin
      return medio
    end else begin
      if (A[medio] < objetivo) then begin
        izq 🡨 medio + 1
      end else begin
        der 🡨 medio - 1
      end
    end
  end
  
  return -1
end
```

## 🧪 Testing

El proyecto incluye tests automatizados con pytest para validar el parsing de Python y pseudocódigo.

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/ -v

# Solo tests de Python
pytest tests/test_ast_builder.py -v

# Solo tests de pseudocódigo
pytest tests/test_psc_parser.py -v

# Con coverage
pytest tests/ --cov=app --cov-report=html
```

### Cobertura de Tests

**Python Parser (7 tests):**
- ✅ `test_sum_array_with_for` - Arrays y loops
- ✅ `test_binary_search_with_while_if` - While e if anidados
- ✅ `test_factorial_recursive` - Recursión
- ✅ `test_unsupported_range_with_step` - Validación de errores
- ✅ `test_unsupported_chained_comparison` - Validación de errores
- ✅ `test_invalid_python_syntax` - Manejo de sintaxis inválida
- ✅ `test_unsupported_tuple_unpacking` - Validación de restricciones

**Pseudocode Parser (8 tests):**
- ✅ `test_sum_array_with_for` - For loops y arrays
- ✅ `test_factorial_with_if` - If-else recursivo
- ✅ `test_binary_search_with_while` - While loops complejos
- ✅ `test_nested_loops` - Loops anidados
- ✅ `test_call_statement` - Llamadas a funciones
- ✅ `test_comparison_operators` - Todos los operadores (`<`, `>`, `<=`, `>=`, `=`, `!=`)
- ✅ `test_repeat_until` - Repeat-until loops
- ✅ `test_invalid_pseudocode` - Manejo de errores

**Total: 15/15 tests pasando** ✅

### Ejemplo de Ejecución

```bash
$ pytest tests/ -v

======================== test session starts =========================
collected 15 items

tests/test_ast_builder.py::test_sum_array_with_for PASSED      [  6%]
tests/test_ast_builder.py::test_binary_search_with_while_if PASSED [ 13%]
tests/test_ast_builder.py::test_factorial_recursive PASSED     [ 20%]
tests/test_ast_builder.py::test_unsupported_range_with_step PASSED [ 26%]
tests/test_ast_builder.py::test_unsupported_chained_comparison PASSED [ 33%]
tests/test_ast_builder.py::test_invalid_python_syntax PASSED   [ 40%]
tests/test_ast_builder.py::test_unsupported_tuple_unpacking PASSED [ 46%]
tests/test_psc_parser.py::test_sum_array_with_for PASSED       [ 53%]
tests/test_psc_parser.py::test_factorial_with_if PASSED        [ 60%]
tests/test_psc_parser.py::test_binary_search_with_while PASSED [ 66%]
tests/test_psc_parser.py::test_nested_loops PASSED             [ 73%]
tests/test_psc_parser.py::test_call_statement PASSED           [ 80%]
tests/test_psc_parser.py::test_comparison_operators PASSED     [ 86%]
tests/test_psc_parser.py::test_repeat_until PASSED             [ 93%]
tests/test_psc_parser.py::test_invalid_pseudocode PASSED       [100%]

======================== 15 passed in 1.2s ==========================
```

## 🧪 Modelos de Datos (Pydantic Schemas)

### `InputRequest`
Request body para endpoints `/normalize` y `/generate-code`:
```python
{
  "content": str,              # Descripción o pseudocódigo (1-10000 chars)
  "input_type": Optional[str]  # "natural_language" o "pseudocode" (auto-detect)
}
```

### `PseudocodeResponse`
Respuesta de `/normalize`:
```python
{
  "original_content": str,
  "normalized_pseudocode": str,
  "input_type_detected": str,
  "is_valid_pseudocode": bool,
  "correction_applied": bool
}
```

### `GenerateRequest`
Request body para `/generate`:
```python
{
  "description": str,     # Descripción del algoritmo
  "filename": Optional[str]  # Nombre del archivo (default: alg_timestamp.py)
}
```

## 🔐 Variables de Entorno

| Variable | Descripción | Valor por defecto | Requerido |
|----------|-------------|-------------------|-----------|
| `GEMINI_API_KEY` | API key de Google Gemini | - | ✅ Sí |
| `HOST` | Host del servidor | `localhost` | ❌ No |
| `PORT` | Puerto del servidor | `8000` | ❌ No |
| `DEBUG` | Modo debug (auto-reload) | `True` | ❌ No |
| `MAX_INPUT_LENGTH` | Longitud máxima de entrada | `10000` | ❌ No |
| `TIMEOUT_SECONDS` | Timeout para operaciones | `30` | ❌ No |

## 🛠️ Stack Técnico Detallado

### Core Framework
- **FastAPI 0.104.1**: Framework web moderno y rápido
- **Uvicorn 0.24.0**: ASGI server para FastAPI
- **Pydantic 2.5.0**: Validación de datos y schemas

### IA y Generación
- **google-generativeai 0.3.2**: Cliente oficial de Gemini API
- **Modelo**: Gemini 2.5 Pro (más reciente y potente)

### Parsing y Gramática
- **Lark 1.1.8**: Parser de gramáticas formales (EBNF)
- Gramática personalizada en `app/grammar/pseudocode.lark`

### Configuración
- **python-decouple 3.8**: Manejo de variables de entorno
- **python-multipart 0.0.6**: Soporte para form data

## 🔮 Roadmap y Estado Actual

### ✅ Fase 1: Generación de Código (COMPLETADO)
- [x] Integración con Gemini 2.5 Pro
- [x] Endpoint `/normalize` - Natural language → Pseudocódigo
- [x] Endpoint `/generate-code` - Generación Python
- [x] Endpoint `/generate` - Generación y guardado automático
- [x] Gramática formal Lark para pseudocódigo
- [x] Documentación completa de API con Swagger

### ✅ Fase 1.5: Parsing y AST (COMPLETADO) 
- [x] Parser Python → IR unificada
- [x] Parser Pseudocódigo → IR unificada
- [x] Endpoint `/ast` - Construcción de AST
- [x] Soporte para declaraciones de variables
- [x] Soporte para asignaciones a arrays multidimensionales
- [x] Sintaxis flexible (con/sin `procedimiento`)
- [x] Manejo de comentarios `►`
- [x] Tests completos (15/15 passing)
- [x] Documentación técnica detallada

**Mejoras Recientes del Parser:**
- ✅ Regla `lvalue` para asignaciones a arrays: `A[i] 🡨 valor`
- ✅ Reglas `then_part`/`else_part` para separación correcta de bloques
- ✅ Soporte `var_declaration` para declaraciones: `i, j, k`
- ✅ Ambas sintaxis: `procedimiento func()` y `func()`
- ✅ Paréntesis opcionales en condiciones: `if (x > 0)` o `if x > 0`

### 🔄 Fase 2: Análisis de Complejidad (En Progreso)
- [ ] Implementar visitor pattern para recorrer AST
- [ ] Calcular complejidades: O(), Ω(), Θ()
- [ ] Integrar Sympy para resolver recurrencias
- [ ] Detectar estructuras anidadas y multiplicar complejidades
- [ ] Análisis de casos: mejor, promedio, peor
- [ ] Detección de recursión (directa e indirecta)

### 📋 Fase 3: Visualización (Planeado)
- [ ] Generar diagramas de flujo con Graphviz
- [ ] Visualizar árboles de recursión
- [ ] Timeline de ejecución paso a paso
- [ ] Gráficas de comparación de complejidades
- [ ] Export a diferentes formatos (PNG, SVG, PDF)

### 🌐 Fase 4: Frontend Web (Planeado)
- [ ] Interfaz React/Vue para facilitar uso
- [ ] Editor de código con syntax highlighting
- [ ] Vista previa del pseudocódigo generado
- [ ] Dashboard de análisis de complejidad
- [ ] Comparador de algoritmos lado a lado

### 🚀 Mejoras Adicionales (Futuro)
- [ ] Cache de respuestas de Gemini (Redis)
- [ ] Sistema de usuarios y autenticación
- [ ] Historial de algoritmos generados
- [ ] Exportar a PDF/Markdown
- [ ] API de traducción entre lenguajes
- [ ] Sugerencias de optimización
- [ ] Detección de patrones algorítmicos

## 🐛 Troubleshooting

### Error: "GEMINI_API_KEY no definida"
**Solución**: Verifica que el archivo `.env` existe y contiene tu API key:
```bash
echo "GEMINI_API_KEY=tu_api_key_aqui" > .env
```

### Error: "Module not found"
**Solución**: Asegúrate de instalar todas las dependencias:
```bash
pip install -r requirements.txt
```

### El servidor no inicia
**Solución**: Verifica que el puerto 8000 no esté en uso:
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

### Respuestas lentas de Gemini
**Solución**: Es normal, la API puede tardar 5-15 segundos. Considera implementar:
- Cache de respuestas
- Indicador de "loading" en el cliente
- Aumentar `TIMEOUT_SECONDS` en `.env`

## 👥 Contribuciones

Este proyecto está siendo desarrollado como parte del curso de **Análisis y Diseño de Algoritmos** en la Universidad, con enfoque en:
- 🎓 Técnicas de parsing formal y gramáticas
- 🤖 Integración práctica de LLMs en aplicaciones reales
- 📊 Análisis algorítmico y complejidad computacional
- 💻 Buenas prácticas de desarrollo con Python/FastAPI

### Desarrolladores
- **Juan González** - [@JuanGonzalezx](https://github.com/JuanGonzalezx)
- **Jhon Patiño** - [@Jhonder18](https://github.com/Jhonder18)

## 📄 Licencia

Este proyecto es académico y está disponible para fines educativos.

---

## 🚀 Quick Start (TL;DR)

```bash
# 1. Clonar
git clone https://github.com/JuanGonzalezx/Algorithms_Proyect.git
cd Algorithms_Proyect

# 2. Instalar
pip install -r requirements.txt

# 3. Configurar .env
echo "GEMINI_API_KEY=tu_api_key" > .env

# 4. Ejecutar
python main.py

# 5. Abrir navegador
# http://localhost:8000/docs
```

---

## 📝 Changelog

### v1.1.0 - Parser de Pseudocódigo Mejorado (Octubre 2025)
**Nuevas Características:**
- ✨ Sintaxis flexible: Soporte para `procedimiento func()` y `func()` directamente
- ✨ Declaraciones de variables: `i, j, k, temp` (parseadas pero ignoradas en AST)
- ✨ Asignaciones a arrays multi-dimensionales: `matriz[i][j] 🡨 valor`
- ✨ Paréntesis opcionales en condiciones: `if (x > 0)` o `if x > 0`
- ✨ Comentarios ignorados correctamente: `► Este es un comentario`

**Mejoras Técnicas:**
- 🔧 Regla `lvalue` para manejar asignaciones complejas
- 🔧 Reglas `then_part`/`else_part` para bloques correctos en if-else
- 🔧 Transformer actualizado para filtrar declaraciones None
- 🔧 Soporte completo para código generado por `/normalize`

**Tests:**
- ✅ 15/15 tests pasando (7 Python + 8 Pseudocódigo)
- ✅ Nuevos tests para SelectionSort completo
- ✅ Validación de estructuras complejas

**Documentación:**
- 📖 README actualizado con ejemplos completos
- 📖 Sección de gramática expandida
- 📖 Flujos de parsing documentados

### v1.0.0 - AST y Parsing Inicial (Octubre 2025)
**Lanzamiento Inicial:**
- 🚀 Endpoint `/api/v1/ast` para construcción de AST
- 🐍 Parser Python → IR con AST nativo
- 📝 Parser Pseudocódigo → IR con Lark
- 🌳 Representación Intermedia unificada (dataclasses)
- 📋 7 tests Python + 8 tests Pseudocódigo
- 📖 Documentación completa en `docs/`

**Características:**
- ✅ Generación con Gemini 2.5 Pro
- ✅ Normalización lenguaje natural → pseudocódigo
- ✅ Generación de código Python ejecutable
- ✅ Guardado automático de algoritmos
- ✅ API REST completa con FastAPI
- ✅ Validación con Pydantic

---

**⭐ Si te fue útil, considera darle una estrella al repositorio!**