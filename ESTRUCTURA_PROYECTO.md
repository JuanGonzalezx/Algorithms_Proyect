# 📁 Estructura del Proyecto Reorganizada

## 🎯 Vista General

```
Algorithms_Proyect/
├── 📄 main.py                  # Punto de entrada de la aplicación
├── 📄 README.md                # Documentación principal
├── 📄 requirements.txt         # Dependencias del proyecto
├── 📄 .env                     # Variables de entorno
├── 📄 .gitignore              # Archivos ignorados por Git
│
├── 📂 app/                     # Código fuente principal
│   ├── api/                    # Endpoints FastAPI
│   ├── config/                 # Configuración
│   ├── controllers/            # Controladores
│   ├── core/                   # Lógica central (parser, AST)
│   ├── grammar/                # Gramática de pseudocódigo
│   ├── models/                 # Modelos de datos
│   ├── modules/                # Módulos del sistema
│   └── services/               # Servicios (Gemini, etc.)
│
├── 📂 ejemplos/                # Scripts de ejemplo ✨ NUEVO
│   ├── ejemplo_cost_analyzer.py
│   ├── ejemplo_parser_agent.py
│   ├── ejemplo_series_solver.py
│   ├── demo_completo.py
│   └── ...
│
├── 📂 test/                    # Tests del sistema ✨ NUEVO
│   ├── test_api_costs.py
│   ├── test_parser.py
│   ├── test_cost_analyzer.py
│   ├── test_two_methods.py
│   └── ...
│
├── 📂 debug/                   # Scripts de depuración ✨ NUEVO
│   ├── debug_parser.py
│   ├── debug_solver.py
│   ├── debug_for_costs.py
│   └── ...
│
├── 📂 documentacion/           # Documentación técnica ✨ NUEVO
│   ├── IMPLEMENTACION_AST.md
│   ├── RESUMEN_COSTOS_POR_LINEA.md
│   ├── GEMINI_TIMEOUT_RETRY.md
│   ├── ENDPOINT_ANALYZE.md
│   └── ...
│
├── 📂 docs/                    # Docs adicionales (ya existía)
│   └── ejemplos/
│
└── 📂 tests/                   # Tests originales (pytest)
    ├── __init__.py
    └── test_psc_parser.py
```

## 📊 Resumen de la Reorganización

### ✅ Archivos Movidos

| Origen (raíz) | Destino | Cantidad |
|--------------|---------|----------|
| `ejemplo_*.py`, `demo_*.py`, `ejemplos_*.py` | `ejemplos/` | 9 archivos |
| `test_*.py`, `verify_*.py`, `test_results*.txt` | `test/` | 31 archivos |
| `debug_*.py`, `check_*.py` | `debug/` | 8 archivos |
| `*.md` (excepto README.md) | `documentacion/` | 8 archivos |

### 📂 Nueva Estructura

#### 1. **`ejemplos/`** - Scripts de Demostración
Contiene ejemplos de uso de cada componente del sistema.

#### 2. **`test/`** - Suite de Pruebas
Todos los tests organizados en un solo lugar.

#### 3. **`debug/`** - Herramientas de Depuración
Scripts para diagnosticar problemas específicos.

#### 4. **`documentacion/`** - Documentación Técnica
Toda la documentación excepto el README principal.

## 🚀 Beneficios

### Antes (Raíz del Proyecto)
```
❌ 56+ archivos en la raíz
❌ Difícil encontrar archivos específicos
❌ Mezcla de código, tests, ejemplos y docs
```

### Después (Organizado)
```
✅ Solo 6 archivos en la raíz (main.py, README.md, etc.)
✅ Fácil navegación por categorías
✅ Estructura profesional y escalable
```

## 📖 Cómo Navegar

### Para aprender a usar el proyecto:
```bash
cd ejemplos/
# Ver ejemplos de uso
```

### Para ejecutar tests:
```bash
cd test/
python test_cost_analyzer.py
```

### Para debug:
```bash
cd debug/
python debug_parser.py
```

### Para leer documentación:
```bash
cd documentacion/
# Abrir archivos .md
```

## 🎯 Archivos que Permanecen en la Raíz

- **`main.py`** - Punto de entrada de la aplicación
- **`README.md`** - Documentación principal
- **`requirements.txt`** - Dependencias
- **`.env`** - Variables de entorno
- **`.gitignore`** - Configuración de Git

## 💡 Notas Importantes

1. ✅ Cada carpeta nueva tiene su propio `README.md` explicativo
2. ✅ Los imports en los scripts siguen funcionando (usan paths absolutos o relativos desde raíz)
3. ✅ El `.gitignore` cubre todas las carpetas
4. ✅ La estructura es estándar en proyectos Python

## 🔄 Comandos de Ejecución

### Desde cualquier ubicación:
```bash
# Ejemplos
python ejemplos/ejemplo_cost_analyzer.py

# Tests
python test/test_parser.py

# Debug
python debug/debug_solver.py
```

### Desde la carpeta específica:
```bash
cd ejemplos
python ejemplo_cost_analyzer.py
```

## 📚 Referencias

- [README Principal](README.md)
- [Documentación](documentacion/README.md)
- [Tests](test/README.md)
- [Ejemplos](ejemplos/README.md)
- [Debug](debug/README.md)
