# Analizador de Complejidades Algorítmicas

Sistema inteligente para análisis automático de complejidad computacional de algoritmos escritos en pseudocódigo, asistido por modelos de lenguaje (LLMs).

## 🎯 Objetivo

Diseñar e implementar un sistema que analice algoritmos escritos en pseudocódigo para determinar automáticamente su complejidad en notación O (peor caso), Ω (mejor caso), Θ (caso promedio) y cotas fuertes.

## 🚀 Tecnologías

- **Backend**: FastAPI
- **Parser**: Lark (gramática formal)
- **LLM**: Google Gemini API
- **Álgebra simbólica**: Sympy (próximamente)
- **Python**: 3.10+

## 📁 Estructura del Proyecto

```
Algorithms_Proyect/
├── main.py                    # Punto de entrada FastAPI
├── requirements.txt           # Dependencias
├── .env                      # Variables de entorno
├── app/
│   ├── config/               # Configuración
│   ├── controllers/          # Endpoints FastAPI
│   ├── core/                 # Lógica central (clasificador, parser)
│   ├── grammar/              # Gramática Lark
│   ├── models/               # Modelos Pydantic y AST
│   └── services/             # Servicios (Gemini API)
└── docs/                     # Documentación y ejemplos
```

## 🔧 Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd Algorithms_Proyect
```

2. **Crear entorno virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
   - Copiar `.env` y configurar `GEMINI_API_KEY`

## ▶️ Ejecución

```bash
python main.py
```

El servidor estará disponible en: http://localhost:8000

## 🌐 API Endpoints

### 📋 Documentación automática
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 🔍 Endpoints principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/classify` | POST | Clasifica entrada como pseudocódigo o lenguaje natural |
| `/api/v1/normalize` | POST | Normaliza entrada a pseudocódigo válido |
| `/api/v1/parse` | POST | Parsea pseudocódigo y genera AST |
| `/api/v1/health` | GET | Verificación de salud del servicio |

### 📝 Ejemplo de uso

```bash
curl -X POST "http://localhost:8000/api/v1/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Crea un algoritmo que calcule el factorial de un número",
    "input_type": "natural_language"
  }'
```

## 🔄 Flujo del Sistema

1. **Entrada**: Usuario proporciona pseudocódigo o descripción en lenguaje natural
2. **Clasificación**: Sistema detecta automáticamente el tipo de entrada
3. **Normalización**: 
   - Si es lenguaje natural → Gemini lo convierte a pseudocódigo
   - Si es pseudocódigo con errores → Gemini lo corrige
4. **Parsing**: Lark parsea el pseudocódigo usando gramática formal
5. **AST**: Se genera árbol sintáctico abstracto
6. **Análisis**: (Próxima fase) Análisis de complejidad con Sympy

## 📖 Gramática Soportada

### Estructuras básicas:
- **Procedimientos**: `nombre(parametros) begin ... end`
- **Asignaciones**: `variable 🡨 valor`
- **Bucles for**: `for variable 🡨 inicio to fin do begin ... end`
- **Bucles while**: `while (condicion) do begin ... end`
- **Condicionales**: `if (condicion) then begin ... end else begin ... end`
- **Llamadas**: `CALL nombre_funcion(parametros)`

### Ejemplos válidos:
Ver `docs/ejemplos/ejemplos_prueba.md`

## 🔮 Próximas Fases

1. **Análisis de Complejidad**: Implementar visitor pattern para calcular complejidades
2. **Resolución de Recurrencias**: Integrar Sympy para resolver ecuaciones recursivas
3. **Visualización**: Diagramas de seguimiento y árboles de recursión
4. **Interfaz Web**: Frontend para facilitar el uso

## 👥 Desarrollo

Este proyecto está siendo desarrollado como parte del curso de Análisis y Diseño de Algoritmos, con enfoque en:
- Técnicas de parsing formal
- Integración de LLMs
- Análisis algorítmico automatizado
- Buenas prácticas de desarrollo