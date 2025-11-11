
# Estructura del proyecto y guía de archivos

Este documento describe la estructura actual del proyecto **Analizador de Complejidades Algorítmicas** y el propósito de cada carpeta/archivo.

---

## Árbol de carpetas (resumen)

```
.
├─ .env
├─ main.py
└─ app/
   ├─ api/
   │  ├─ __init__.py
   │  ├─ analyzer_controller.py
   │  └─ routes.py
   ├─ config/
   │  ├─ __init__.py
   │  └─ settings.py
   ├─ modules/
   │  ├─ __init__.py
   │  ├─ analyzer/
   │  │  └─ ... (costos)
   │  ├─ parser/
   │  │  └─ ... (parser)
   │  ├─ solver/
   │  │  └─ ... (solver de series)
   │  └─ syntax_validator/
   │     └─ ... (validador sintáctico)
   ├─ services/
   │  ├─ __init__.py
   │  ├─ ast_nodes.py
   │  ├─ ast_service.py
   │  ├─ gemini_service.py
   │  └─ psc_parser.py
   └─ shared/
      ├─ __init__.py
      ├─ models.py
      └─ grammar/
         ├─ __init__.py
         └─ pseudocode.lark
```

> **Docs:** Swagger en **`/docs`** y ReDoc custom en **`/redoc`** (configurados en `main.py`).

---

## Flujo de alto nivel (pipeline)

1. **syntax_validator** (`app/modules/syntax_validator`): normaliza y valida el pseudocódigo.
2. **parser** (`app/modules/parser`): convierte el pseudocódigo válido a **AST/IR** (usando la gramática `shared/grammar/pseudocode.lark`).
3. **analyzer** (`app/modules/analyzer`): recorre el AST y produce **sumatorias de costo** (por nodo y por línea).
4. **solver** (`app/modules/solver`): resuelve/simplifica las sumatorias (SymPy) y entrega **costos exactos y cotas Ω/Θ/O**.

El **API** orquesta este pipeline desde `app/api/routes.py` en los endpoints `/api/v1/*`.

---

## Archivos principales

### Raíz
- **`main.py`**
  - Punto de entrada FastAPI.
  - Configura CORS, Swagger (`/docs`), ReDoc custom (`/redoc`), y monta routers.
  - Lee configuración desde `app/config/settings.py` (incluyendo API keys).
  - Endpoints de salud: `/` y `/health`.

- **`.env`**
  - Variables de entorno (p. ej. `HOST`, `PORT`, `DEBUG`, `GEMINI_API_KEY(S)`).
  - Cargadas por `settings.py` vía Pydantic Settings.

---

### `app/api/` (capa HTTP)
- **`__init__.py`**
  - Marca el paquete.

- **`routes.py`**
  - **Endpoint principales** (documentado en Swagger):
    - `POST /api/v1/validate-syntax` → usa `syntax_validator`
    - `POST /api/v1/parse` → usa `parser`
    - `POST /api/v1/costs` → usa `analyzer`
    - `POST /api/v1/solve` → usa `solver`
    - `POST /api/v1/analyze` → **pipeline completo** (NL → Pseudocódigo → AST → Costos → Big-O)
  - `GET /api/v1/health` para health-check.

- **`analyzer_controller.py`**
  - Endpoints utilitarios para integración con LLM (Gemini) y AST directo:
    - `POST /api/v1/generate` (genera y guarda código a partir de descripción)
    - `POST /api/v1/normalize` (normaliza a pseudocódigo con Gemini)
    - `POST /api/v1/generate-code` (solo genera código)
    - `POST /api/v1/ast` (construye AST desde pseudocódigo)
  - Nota: usa `gemini_service.py` cuando corresponde.

---

### `app/config/` (configuración)
- **`__init__.py`**
  - Paquete.

- **`settings.py`**
  - Configuración central (Pydantic `BaseSettings`).
  - Expone `settings` con atributos: `HOST`, `PORT`, `DEBUG`, `GEMINI_API_KEY`/`GEMINI_API_KEYS`, etc.

---

### `app/modules/`
- **`__init__.py`**
  - Paquete.

- **`analyzer/`**
  - Implementa el **Cost Analyzer** (p. ej. `validador.py` / `cost_model.py`):
    - Reglas de costo por nodo (For/While/If/Assign…).
    - Generación de costos **por nodo** y **por línea**.
    - Exporta `get_cost_analyzer()`.

- **`parser/`**
  - Agente Parser:
    - Wrappea `psc_parser.py` y la gramática `pseudocode.lark`.
    - Devuelve `Program` (IR) con `to_dict()`.
    - Exporta `get_parser_agent()`.

- **`solver/`**
  - Resolver de series (SymPy):
    - Simplifica sumatorias y genera costos exactos.
    - Calcula **Big‑O**, **Theta** y **Omega**.
    - Exporta `get_series_solver()`.

- **`syntax_validator/`**
  - Validador y normalizador ligero:
    - Heurísticas y limpiezas mínimas del pseudocódigo.
    - Puede enriquecer metadatos (líneas, conteos, etc.).
    - Exporta `get_syntax_validator()`.

---

### `app/services/` (infra/servicios compartidos)
- **`__init__.py`**
  - Paquete.

- **`ast_nodes.py`**
  - **IR/AST del proyecto** (dataclasses): `Program`, `Function`, `Block`, `Stmt`, `Expr`, etc.
  - Cada nodo implementa `to_dict()` para serialización.

- **`ast_service.py`**
  - Utilidades para construir/serializar AST fuera del flujo.
  - **Nota**: Si `routes.py` ya orquesta todo, este módulo puede considerarse **de soporte** o **legacy**.

- **`gemini_service.py`**
  - Cliente para Gemini (normalización de pseudocódigo y generación de código).
  - Respetar claves desde `settings.py`.

- **`psc_parser.py`**
  - Parser Lark + Transformer → construye `Program` (IR) desde pseudocódigo.
  - Carga gramática desde `shared/grammar/pseudocode.lark`.

---

### `app/shared/` (modelos y recursos comunes)
- **`__init__.py`**
  - Paquete.

- **`models.py`**
  - **Modelos Pydantic compartidos**:
    - Entrada/salida del API (`PseudocodeIn`, `SyntaxValidationResult`, `ASTResult`, …)
    - Estructuras del analizador (`CostExpr`, `NodeCost`, `CostsOut`, …)
    - Resultado del solver (`SolveOut`, `AsymptoticBounds`, `ExactCosts`, …)
    - Paquete para la **respuesta completa** (`CompleteAnalysisResult`).

- **`grammar/`**
  - **`pseudocode.lark`**: gramática del pseudocódigo (tokens, reglas y precedencias).
  - `__init__.py` para importar como paquete si hace falta.

---

## Endpoints importantes (resumen)

- **Swagger UI**: `GET /docs`
- **ReDoc**: `GET /redoc`
- **OpenAPI JSON**: `GET /openapi.json`

- **Validación**: `POST /api/v1/validate-syntax`
- **Parsing**: `POST /api/v1/parse`
- **Costos**: `POST /api/v1/costs`
- **Pipeline completo**: `POST /api/v1/analyze`
- **Solver directo**: `POST /api/v1/solve`
- **AST directo**: `POST /api/v1/ast` (controlador utilitario)
- **Normalización con LLM**: `POST /api/v1/normalize` (controlador utilitario)
- **Generación de código (LLM)**: `POST /api/v1/generate` / `POST /api/v1/generate-code`

---

## Notas de mantenimiento

- Si **no** usas Gemini, puedes deshabilitar endpoints utilitarios del `analyzer_controller.py`.
- Para evitar confusiones, procura que **todas las rutas de análisis** usen el pipeline de `app/api/routes.py`.
- Mantén la gramática en `shared/grammar/pseudocode.lark` sincronizada con el Transformer en `psc_parser.py`.
- Cuando cambies el IR (`ast_nodes.py`), ajusta el analyzer y el solver en consecuencia.
- Revisa imports relativos/absolutos para evitar `ModuleNotFoundError` al ejecutar `main.py` desde la raíz del repo.
