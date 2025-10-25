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
│   ├── core/                        # 🧠 Lógica central (futuro)
│   ├── grammar/
│   │   └── pseudocode.lark          # 📝 Gramática formal del pseudocódigo
│   ├── models/
│   │   ├── ast_nodes.py             # 🌳 Nodos del AST
│   │   └── schemas.py               # 📋 Modelos Pydantic
│   └── services/
│       ├── __init__.py
│       └── gemini_service.py        # 🤖 Integración con Gemini AI
└── docs/
    └── ejemplos/
        ├── ejemplos_prueba.md       # 📖 Ejemplos de uso
        └── algoritmos_guardados/    # 💾 Códigos generados (auto-creado)
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

## 🔄 Flujo del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    Usuario envía descripción                     │
│              (Lenguaje natural o pseudocódigo)                   │
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
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               Gemini Service (services/)                         │
│          - normalize_to_pseudocode()                             │
│          - generate_python_code()                                │
│          Usa prompts especializados + Gemini 2.5 Pro             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Google Gemini AI API                            │
│           Procesa y genera respuesta inteligente                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Respuesta al usuario (JSON)                         │
│      - Pseudocódigo estructurado (con 🡨 para asignaciones)       │
│      - Código Python ejecutable                                  │
│      - Archivo guardado (opcional)                               │
└─────────────────────────────────────────────────────────────────┘
```

## 📖 Gramática de Pseudocódigo Soportada

El sistema genera pseudocódigo siguiendo estas reglas formales:

### Estructuras Básicas:

| Estructura | Sintaxis | Ejemplo |
|------------|----------|---------|
| **Procedimiento** | `nombre(params) begin ... end` | `factorial(n) begin ... end` |
| **Asignación** | `variable 🡨 valor` | `suma 🡨 0` |
| **For Loop** | `for var 🡨 inicio to fin do begin ... end` | `for i 🡨 1 to n do begin ... end` |
| **While Loop** | `while (condicion) do begin ... end` | `while (i < n) do begin ... end` |
| **Repeat Until** | `repeat ... until (condicion)` | `repeat ... until (suma > 100)` |
| **Condicional** | `if (cond) then begin ... end else begin ... end` | `if (x > 0) then begin ... end` |
| **Llamada** | `CALL funcion(params)` | `CALL ordenar(A, n)` |
| **Arreglos** | `A[i]` o `A[i..j]` | `A[1]`, `A[1..n]` |
| **Comentario** | `► texto` | `► Este es un comentario` |
| **Booleanos** | `T`, `F` | `esPar 🡨 T` |

### Operadores:
- **Aritméticos**: `+`, `-`, `*`, `/`, `mod`, `div`
- **Lógicos**: `and`, `or`, `not`
- **Relacionales**: `<`, `>`, `≤`, `≥`, `=`, `≠`

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

## 🔮 Próximas Fases y Roadmap

### Fase 2: Análisis de Complejidad (En desarrollo)
- [ ] Implementar visitor pattern para recorrer AST
- [ ] Calcular complejidades: O(), Ω(), Θ()
- [ ] Integrar Sympy para resolver recurrencias
- [ ] Detectar estructuras anidadas y multiplicar complejidades

### Fase 3: Visualización
- [ ] Generar diagramas de flujo con Graphviz
- [ ] Visualizar árboles de recursión
- [ ] Timeline de ejecución paso a paso
- [ ] Gráficas de comparación de complejidades

### Fase 4: Frontend Web
- [ ] Interfaz React/Vue para facilitar uso
- [ ] Editor de código con syntax highlighting
- [ ] Vista previa del pseudocódigo generado
- [ ] Dashboard de análisis de complejidad

### Mejoras Adicionales
- [ ] Cache de respuestas de Gemini (Redis)
- [ ] Sistema de usuarios y autenticación
- [ ] Historial de algoritmos generados
- [ ] Exportar a PDF/Markdown
- [ ] Tests unitarios y de integración

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

**⭐ Si te fue útil, considera darle una estrella al repositorio!**