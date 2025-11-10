# 🧪 Tests del Proyecto

Esta carpeta contiene todos los archivos de prueba del sistema.

## 🎯 Contenido

### Tests de API
- **`test_api_costs.py`** - Tests de endpoints de costos
- **`test_api_syntax.py`** - Tests de validación sintáctica
- **`test_ast_endpoint.py`** - Tests del endpoint AST
- **`test_endpoint.py`** - Tests generales de endpoints
- **`test_endpoint_linecosts.py`** - Tests de costos por línea
- **`test_complete_endpoint.py`** - Tests del endpoint completo

### Tests de Componentes
- **`test_parser.py`** - Tests del parser de pseudocódigo
- **`test_cost_analyzer.py`** - Tests del analizador de costos
- **`test_series_solver.py`** - Tests del solver de sumatorias
- **`test_syntax_validator.py`** - Tests del validador sintáctico

### Tests de Funcionalidades
- **`test_two_methods.py`** - Test de los dos métodos de resolución (por bloques y por líneas)
- **`test_bubble_lines.py`** - Test de burbuja con costos por línea
- **`test_line_info.py`** - Test de información por línea
- **`test_selection_sort.py`** - Test de ordenamiento por selección
- **`test_array_assign.py`** - Test de asignaciones de arrays
- **`test_pseudocode.py`** - Tests de pseudocódigo
- **`test_clean_ast.py`** - Tests de limpieza de AST
- **`test_detection.py`** - Tests de detección de lenguaje
- **`test_new_features.py`** - Tests de nuevas características
- **`test_complete_features.py`** - Tests de características completas
- **`test_final_linecosts.py`** - Tests finales de costos por línea
- **`test_selection_minimal.py`** - Test minimal de selección

### Tests de Gemini
- **`test_gemini_api.py`** - Test de conexión con Gemini API
- **`test_gemini_retry.py`** - Test de reintentos de Gemini

### Scripts de Verificación
- **`verify_complete.py`** - Verificación completa del sistema
- **`verify_imports.py`** - Verificación de imports
- **`verify_solver.py`** - Verificación del solver

### Archivos de Resultados
- **`test_results.txt`** - Resultados de pruebas
- **`test_results2.txt`** - Resultados adicionales
- **`test_results3.txt`** - Más resultados
- **`output_test.txt`** - Output de tests

## 🚀 Cómo Ejecutar

### Ejecutar todos los tests
```bash
pytest test/
```

### Ejecutar un test específico
```bash
python test/test_cost_analyzer.py
```

### Ejecutar con verbose
```bash
python test/test_series_solver.py -v
```
