# 📁 Estructura del Proyecto

## 🎯 Vista General

```
Algorithms_Proyect/
├── 📄 main.py                  # Punto de entrada de la aplicación
├── 📄 README.md                # Documentación principal
├── 📄 requirements.txt         # Dependencias del proyecto
├── 📄 .env                     # Variables de entorno (no versionado)
├── 📄 .env.example            # Plantilla de configuración
├── 📄 .gitignore              # Archivos ignorados por Git
│
├── 📂 app/                     # Código fuente principal
│   ├── api/                    # Endpoints FastAPI
│   │   ├── __init__.py
│   │   └── routes.py           # Rutas del API
│   ├── config/                 # Configuración
│   │   ├── __init__.py
│   │   └── settings.py         # Variables de entorno
│   ├── controllers/            # Controladores (legacy)
│   ├── core/                   # Lógica central (legacy)
│   │   ├── psc_parser.py
│   │   └── py_ast_builder.py
│   ├── grammar/                # Gramática de pseudocódigo
│   │   └── pseudocode.lark
│   ├── models/                 # Modelos de datos
│   │   └── ast_nodes.py
│   ├── modules/                # ✨ Arquitectura modular de agentes
│   │   ├── syntax_validator/   # Agente 1: Validación sintáctica
│   │   ├── parser/             # Agente 2: Parser (Lark → AST)
│   │   ├── analyzer/           # Agente 3: Análisis de costos
│   │   └── solver/             # Agente 4: Resolución de sumatorias
│   ├── services/               # Servicios externos
│   │   └── gemini_service.py   # Integración con Gemini API
│   └── shared/                 # Recursos compartidos
│       ├── models.py           # Modelos Pydantic
│       └── grammar/            # Gramáticas compartidas
│
└── 📂 tests/                   # Tests unitarios (pytest)
    ├── __init__.py
    └── test_psc_parser.py
```

## 📊 Arquitectura del Sistema

### 🔧 Módulos Principales

#### 1. **`app/modules/`** - Arquitectura de 4 Agentes
Sistema modular con agentes independientes siguiendo el patrón de arquitectura de agentes:

- **`syntax_validator/`**: Valida y normaliza pseudocódigo
- **`parser/`**: Convierte pseudocódigo a AST custom usando Lark
- **`analyzer/`**: Analiza costos computacionales (genera sumatorias)
- **`solver/`**: Resuelve sumatorias y calcula Big-O con SymPy

#### 2. **`app/api/`** - Endpoints REST
- `POST /api/v1/analyze`: Endpoint principal de análisis completo
- Detección automática de lenguaje natural vs pseudocódigo
- Integración con Gemini API para normalización

#### 3. **`app/services/`** - Servicios Externos
- **Gemini Service**: Multi-key rotation, timeout/retry automático
- Soporte para `gemini-2.5-flash` con manejo de cuota

#### 4. **`app/shared/`** - Recursos Compartidos
- Modelos Pydantic para validación y serialización
- Gramáticas Lark compartidas

### 📁 Estructura Organizada

#### **`tests/`** - Tests Unitarios
Suite de tests con pytest para validar funcionalidad del parser.

## 🚀 Características Principales

### ✅ Sistema Completo de Análisis de Algoritmos
```
✅ Detección automática de lenguaje natural vs pseudocódigo
✅ Normalización con Gemini API (GPT para pseudocódigo)
✅ Validación sintáctica con Lark
✅ Generación de AST custom optimizado
✅ Análisis de costos por línea y por bloque
✅ Resolución de sumatorias con pasos detallados
✅ Cálculo de Big-O, Omega y Theta
✅ API REST con FastAPI + Swagger UI
```

### 🔥 Ventajas de la Arquitectura
```
✅ Modular: Cada agente es independiente y reutilizable
✅ Testeable: Tests unitarios para cada componente
✅ Escalable: Fácil agregar nuevos agentes o modificar existentes
✅ Resiliente: Manejo de errores, timeouts y rotación de API keys
✅ Documentado: Documentación completa de cada agente
```

## 📖 Guía Rápida

### Iniciar el servidor:
```bash
python -m uvicorn main:app --reload --host localhost --port 8000
```

### Acceder a la documentación interactiva:
```
http://localhost:8000/docs
```

### Ejecutar tests:
```bash
cd tests/
pytest test_psc_parser.py -v
```

### Probar endpoint:
```bash
# El servidor debe estar corriendo
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "ordenamiento burbuja"}'
```

## 🎯 Archivos en la Raíz

- **`main.py`** - Punto de entrada de la aplicación FastAPI
- **`README.md`** - Documentación principal del proyecto
- **`requirements.txt`** - Dependencias del proyecto
- **`.env`** - Variables de entorno (no versionado, usar `.env.example`)
- **`.env.example`** - Plantilla de configuración
- **`.gitignore`** - Archivos ignorados por Git

## � Endpoints del API

### POST `/api/v1/analyze`
Endpoint principal que analiza algoritmos completos.

**Input:**
```json
{
  "text": "Ordena un arreglo usando burbuja",
  "language_hint": "es"
}
```

**Output:**
```json
{
  "input_text": "...",
  "validation": { ... },
  "ast": { ... },
  "costs": {
    "per_line": [...],
    "per_node": [...],
    "total": { "best": "...", "avg": "...", "worst": "..." }
  },
  "solution": {
    "exact": { "best": "n²+n-1", ... },
    "big_o": { "best": "O(n²)", ... },
    "bounds": { "omega": "Ω(n²)", "theta": "Θ(n²)", "big_o": "O(n²)" },
    "steps_by_line": [...]
  }
}
```

## 💡 Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **Lark**: Parser de gramáticas context-free
- **SymPy**: Cálculo simbólico y resolución de sumatorias
- **Pydantic**: Validación de datos y serialización
- **Google Gemini API**: Normalización de lenguaje natural
- **Python 3.11+**: Lenguaje base

## 📚 Referencias

- [Tests Unitarios](tests/)
- [Swagger UI](http://localhost:8000/docs) - Documentación interactiva del API
- [README Principal](README.md) - Información general del proyecto
