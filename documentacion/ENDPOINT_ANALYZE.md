# Endpoint `/api/v1/analyze` - Análisis Completo

## 📝 Descripción

**Endpoint principal para el frontend**: Un solo botón, una sola petición, toda la información.

Acepta **lenguaje natural** o **pseudocódigo** y devuelve el análisis completo de complejidad algorítmica.

---

## 🚀 Características

### Detección Automática de Tipo de Entrada

El endpoint detecta automáticamente si el texto es:
- **Lenguaje Natural**: "Quiero un algoritmo que ordene un arreglo"
- **Pseudocódigo**: `procedimiento burbuja(A, n) begin...`

### Pipeline Completo (4-5 Agentes)

#### Si es Lenguaje Natural (5 etapas):
1. 🤖 **Normalización con Gemini**: Convierte lenguaje natural → pseudocódigo
2. 🔍 **Validación sintáctica**: Valida y corrige el pseudocódigo
3. 🌳 **Generación de AST**: Construye el árbol de sintaxis abstracta
4. 📊 **Análisis de costos**: Genera sumatorias (sin resolver)
5. 🎯 **Resolución**: Resuelve sumatorias y calcula Big-O, Ω, Θ, O

#### Si es Pseudocódigo (4 etapas):
1. 🔍 **Validación sintáctica**: Valida y corrige el pseudocódigo
2. 🌳 **Generación de AST**: Construye el árbol de sintaxis abstracta
3. 📊 **Análisis de costos**: Genera sumatorias (sin resolver)
4. 🎯 **Resolución**: Resuelve sumatorias y calcula Big-O, Ω, Θ, O

---

## 📥 Request

### Endpoint
```
POST /api/v1/analyze
```

### Headers
```json
{
  "Content-Type": "application/json"
}
```

### Body (JSON)
```json
{
  "text": "Quiero un algoritmo que ordene un arreglo usando bubble sort",
  "language_hint": "es"
}
```

#### Parámetros:
- `text` (string, requerido): Texto en lenguaje natural o pseudocódigo
- `language_hint` (string, opcional): Idioma ("es" o "en"), por defecto "es"

---

## 📤 Response

### Estructura Completa (JSON)

```json
{
  "input_text": "Quiero un algoritmo...",
  
  "validation": {
    "era_algoritmo_valido": true,
    "codigo_corregido": "procedimiento burbuja(A, n)...",
    "errores": [],
    "normalizaciones": ["Reemplazado <- por 🡨"],
    "hints": {}
  },
  
  "ast": {
    "success": true,
    "ast": {
      "type": "Program",
      "functions": [...]
    },
    "metadata": {
      "functions": 1,
      "total_nodes": 8
    }
  },
  
  "costs": {
    "per_node": [
      {
        "node_id": "For_1",
        "node_type": "For",
        "cost": {
          "best": "Sum(...)",
          "avg": "Sum(...)",
          "worst": "Sum(...)"
        }
      }
    ],
    "total": {
      "best": "Sum(Sum(1, (j, 1, (n - i))), (i, 1, (n - 1)))",
      "avg": "Sum(Sum(1 + 0.5*(1 + 1 + 1), (j, 1, (n - i))), (i, 1, (n - 1)))",
      "worst": "Sum(Sum(1 + max(1 + 1 + 1, 0), (j, 1, (n - i))), (i, 1, (n - 1)))"
    }
  },
  
  "solution": {
    "exact": {
      "best": "n*(n - 1)/2",
      "avg": "5*n*(n - 1)/4",
      "worst": "2*n*(n - 1)"
    },
    "big_o": {
      "best": "O(n**2)",
      "avg": "O(n**2)",
      "worst": "O(n**2)"
    },
    "bounds": {
      "omega": "Ω(n**2)",
      "theta": "Θ(n**2)",
      "big_o": "O(n**2)"
    }
  },
  
  "metadata": {
    "pipeline_stages": 5,
    "used_gemini_normalization": true,
    "input_type": "natural_language",
    "total_nodes_analyzed": 8,
    "has_errors": false,
    "normalizations_applied": 1,
    "final_pseudocode": "procedimiento burbuja(A, n)..."
  }
}
```

---

## 🎯 Casos de Uso

### Caso 1: Lenguaje Natural

**Input:**
```json
{
  "text": "Necesito un algoritmo que ordene un arreglo usando el método de burbuja"
}
```

**Flujo:**
1. Detecta lenguaje natural
2. Usa Gemini para generar pseudocódigo
3. Valida y parsea el pseudocódigo generado
4. Analiza costos
5. Calcula Big-O

**Output:**
- `metadata.used_gemini_normalization`: `true`
- `metadata.input_type`: `"natural_language"`
- `metadata.final_pseudocode`: Pseudocódigo generado por Gemini
- Análisis completo de complejidad

---

### Caso 2: Pseudocódigo Directo

**Input:**
```json
{
  "text": "procedimiento burbuja(A, n)\nbegin\n  for i <- 1 to n - 1 do\n  ..."
}
```

**Flujo:**
1. Detecta pseudocódigo
2. Valida y corrige si es necesario
3. Parsea a AST
4. Analiza costos
5. Calcula Big-O

**Output:**
- `metadata.used_gemini_normalization`: `false`
- `metadata.input_type`: `"pseudocode"`
- Análisis completo de complejidad

---

## 🔍 Detección de Tipo de Entrada

### Heurística de Detección

El sistema usa las siguientes reglas para detectar el tipo de entrada:

#### Es Pseudocódigo si:
- Contiene 3+ palabras clave: `procedimiento`, `begin`, `end`, `for`, `while`, `if`, `return`
- Contiene símbolos de asignación: `🡨`, `<-`, `:=`
- Tiene estructura multilínea con bloques

#### Es Lenguaje Natural si:
- Contiene frases descriptivas: "quiero", "necesito", "crea", "implementa"
- Es texto corto (<3 líneas, <200 caracteres)
- No tiene palabras clave de pseudocódigo

---

## 📊 Información Devuelta

### 1. Validación (`validation`)
- Errores de sintaxis
- Código corregido/normalizado
- Normalizaciones aplicadas

### 2. AST (`ast`)
- Árbol completo en formato JSON
- Metadatos: número de funciones, nodos

### 3. Costos (`costs`)
- Costos por nodo (cada `for`, `if`, `while`, etc.)
- Costo total (sumatorias sin resolver)
- Tres casos: best, avg, worst

### 4. Solución (`solution`)
- **Expresiones exactas**: Sumatorias resueltas (ej: `n*(n-1)/2`)
- **Big-O simplificado**: Términos dominantes (ej: `O(n**2)`)
- **Cotas asintóticas**: Ω (lower bound), Θ (tight bound), O (upper bound)

### 5. Metadatos (`metadata`)
- Número de etapas del pipeline
- Si se usó Gemini para normalización
- Tipo de entrada detectado
- Pseudocódigo final analizado

---

## 🧪 Pruebas

### Test con Pseudocódigo
```bash
cd "/ruta/al/proyecto"
.venv/Scripts/python test_complete_endpoint.py
```

### Test con Lenguaje Natural
```bash
.venv/Scripts/python test_complete_endpoint.py --natural
```

### Test de Detección
```bash
.venv/Scripts/python test_detection.py
```

---

## ⚡ Ejemplos de Uso desde Frontend

### JavaScript (Fetch)
```javascript
async function analyzeAlgorithm(userInput) {
  const response = await fetch('http://localhost:8000/api/v1/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      text: userInput,
      language_hint: 'es'
    })
  });
  
  const data = await response.json();
  
  // Mostrar resultados
  console.log('Complejidad:', data.solution.bounds.big_o);
  console.log('Expresión exacta (worst):', data.solution.exact.worst);
  console.log('Pseudocódigo usado:', data.metadata.final_pseudocode);
}
```

### Python (Requests)
```python
import requests

def analyze_algorithm(user_input):
    response = requests.post(
        'http://localhost:8000/api/v1/analyze',
        json={
            'text': user_input,
            'language_hint': 'es'
        }
    )
    
    data = response.json()
    
    print(f"Big-O: {data['solution']['bounds']['big_o']}")
    print(f"Expresión (worst): {data['solution']['exact']['worst']}")
    
    return data
```

---

## 🚨 Manejo de Errores

### Error 400: Sintaxis Inválida
```json
{
  "detail": {
    "message": "El código tiene errores de sintaxis que impiden el análisis",
    "errors": [
      {
        "line": 3,
        "column": 12,
        "detail": "Token inesperado",
        "suggestion": "Verifica la sintaxis del for"
      }
    ]
  }
}
```

### Error 500: Error Interno
```json
{
  "detail": "Error interno durante el análisis: [descripción]"
}
```

---

## 🎨 Integración con Frontend

### Un Solo Botón
```html
<button onclick="analyzeCode()">Analizar Algoritmo</button>

<script>
async function analyzeCode() {
  const userInput = document.getElementById('codeInput').value;
  
  // Mostrar loading
  showLoading();
  
  try {
    const data = await analyzeAlgorithm(userInput);
    
    // Mostrar toda la información
    displayValidation(data.validation);
    displayAST(data.ast);
    displayCosts(data.costs);
    displaySolution(data.solution);
    displayMetadata(data.metadata);
  } catch (error) {
    showError(error);
  } finally {
    hideLoading();
  }
}
</script>
```

---

## 📚 Documentación Relacionada

- **Gramática del pseudocódigo**: `app/grammar/pseudocode.lark`
- **Modelos de datos**: `app/shared/models.py`
- **Servicio de Gemini**: `app/services/gemini_service.py`
- **Cost Analyzer**: `app/modules/analyzer/cost_model.py`
- **Series Solver**: `app/modules/solver/solver.py`

---

## 🔧 Configuración

### Variables de Entorno (`.env`)
```env
GEMINI_API_KEY=tu_api_key_aqui
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### Iniciar Servidor
```bash
python -m uvicorn main:app --reload --port 8000
```

---

## ✅ Resumen

**Un endpoint, todo el análisis:**
- ✅ Acepta lenguaje natural o pseudocódigo
- ✅ Detección automática del tipo de entrada
- ✅ Normalización con Gemini (si es necesario)
- ✅ Validación y corrección sintáctica
- ✅ Generación de AST
- ✅ Análisis de costos (3 casos: best/avg/worst)
- ✅ Resolución de sumatorias
- ✅ Cálculo de Big-O y cotas asintóticas
- ✅ Metadata completo para debugging

**Perfecto para frontend:** Una petición, toda la información necesaria para mostrar al usuario.
