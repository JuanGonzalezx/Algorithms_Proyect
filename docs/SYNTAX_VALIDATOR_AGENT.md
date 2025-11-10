# Agente de Validación Sintáctica

Este módulo implementa el primer agente del sistema: **syntax_validator**, responsable de validar la sintaxis del pseudocódigo usando Lark.

## 📁 Estructura

```
app/
├── modules/
│   └── syntax_validator/
│       ├── __init__.py
│       ├── agent.py          # Lógica del agente
│       └── grammar.lark      # Gramática del pseudocódigo
├── shared/
│   ├── __init__.py
│   └── models.py             # Modelos Pydantic compartidos
├── api/
│   ├── __init__.py
│   └── routes.py             # Endpoints API
└── main.py                   # Aplicación FastAPI
```

## 🚀 Uso

### Como agente standalone

```python
from app.shared.models import PseudocodeIn
from app.modules.syntax_validator.agent import get_syntax_validator

# Obtener el agente
validator = get_syntax_validator()

# Validar código
code = """
procedimiento Ejemplo(n)
begin
    x 🡨 5
    if x > 0 then
    begin
        x 🡨 x + 1
    end
end
"""

input_data = PseudocodeIn(text=code, language_hint="es")
result = validator.validate(input_data)

print(f"Válido: {result.era_algoritmo_valido}")
print(f"Errores: {len(result.errores)}")
print(f"Normalizaciones: {result.normalizaciones}")
```

### Como parte de un grafo LangGraph

```python
from langgraph.graph import StateGraph
from app.modules.syntax_validator.agent import get_syntax_validator

# Definir el estado
class AgentState(TypedDict):
    text: str
    language_hint: str
    era_algoritmo_valido: bool
    codigo_corregido: str
    errores_sintaxis: List[ErrorItem]
    normalizaciones: List[str]

# Crear grafo
workflow = StateGraph(AgentState)

# Añadir el agente
validator = get_syntax_validator()
workflow.add_node("validate_syntax", validator)

# Definir flujo
workflow.set_entry_point("validate_syntax")
# ... añadir más nodos y edges

# Compilar
app = workflow.compile()
```

### Vía API REST

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Validar sintaxis
curl -X POST http://localhost:8000/api/v1/validate-syntax \
  -H "Content-Type: application/json" \
  -d '{
    "text": "x 🡨 5",
    "language_hint": "es"
  }'
```

## 📊 Modelos de Datos

### PseudocodeIn

Entrada para el agente:

```python
{
    "text": str,              # Pseudocódigo a validar
    "language_hint": str      # "es" o "en" (opcional, default: "es")
}
```

### SyntaxValidationResult

Resultado de la validación:

```python
{
    "era_algoritmo_valido": bool,        # True si es válido
    "codigo_corregido": str,             # Código normalizado
    "errores": [ErrorItem],              # Lista de errores encontrados
    "normalizaciones": [str],            # Normalizaciones aplicadas
    "hints": {                           # Metadatos adicionales
        "parser_engine": "lark-lalr",
        "total_errors": int,
        "total_normalizations": int,
        "code_length": int,
        "line_count": int
    }
}
```

### ErrorItem

Detalle de un error:

```python
{
    "linea": int,           # Número de línea (opcional)
    "columna": int,         # Número de columna (opcional)
    "regla": str,           # Regla violada (opcional)
    "detalle": str,         # Descripción del error (opcional)
    "sugerencia": str       # Sugerencia de corrección (opcional)
}
```

## 🔧 Normalizaciones

El agente aplica automáticamente las siguientes normalizaciones:

1. **Saltos de línea**: Convierte CRLF → LF
2. **Espacios finales**: Elimina espacios al final de cada línea
3. **Nueva línea final**: Añade `\n` al final del archivo si falta
4. **Operadores**: Normaliza símbolos de comparación:
   - `<=` → `≤`
   - `>=` → `≥`
   - `!=` → `≠`

## 🧪 Testing

Ejecutar las pruebas:

```bash
python test_syntax_validator.py
```

## 📝 Gramática

La gramática soporta:

- ✅ Declaración de procedimientos
- ✅ Variables y arrays
- ✅ Estructuras de control (for, while, repeat, if-then-else)
- ✅ Asignaciones con `🡨`
- ✅ Expresiones aritméticas y lógicas
- ✅ Operadores especiales (div, mod, ceiling ┌┐, floor └┘)
- ✅ Llamadas a funciones
- ✅ Comentarios con `►`

## 🔄 Integración con LangGraph

El agente implementa el protocolo `__call__` para ser usado en grafos:

```python
def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesa el estado del grafo y retorna el estado actualizado.
    """
    # Extrae input del estado
    # Valida sintaxis
    # Actualiza estado con resultados
    return updated_state
```

## 🎯 Próximos Pasos

Agentes planificados:

1. ✅ **syntax_validator** - Validación sintáctica (ACTUAL)
2. ⏳ **semantic_analyzer** - Análisis semántico
3. ⏳ **complexity_calculator** - Cálculo de complejidad
4. ⏳ **optimizer_suggester** - Sugerencias de optimización

## 📚 Referencias

- [Lark Parser](https://lark-parser.readthedocs.io/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic V2](https://docs.pydantic.dev/latest/)
