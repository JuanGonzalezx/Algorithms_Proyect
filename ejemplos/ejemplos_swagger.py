"""
EJEMPLOS LISTOS PARA COPIAR EN SWAGGER
======================================

Copia y pega estos JSON directamente en Swagger UI
http://localhost:8000/docs
"""

print("\n" + "="*70)
print("🌐 EJEMPLOS PARA SWAGGER UI - Endpoint: POST /api/v1/validate-syntax")
print("="*70)

ejemplos = [
    {
        "nombre": "1. Código Válido Simple",
        "descripcion": "Asignación básica",
        "json": '''{
  "text": "x 🡨 5",
  "language_hint": "es"
}'''
    },
    {
        "nombre": "2. Procedimiento Suma",
        "descripcion": "Procedimiento con parámetros y return",
        "json": '''{
  "text": "procedimiento Suma(a, b)\\nbegin\\n    resultado 🡨 a + b\\n    return resultado\\nend",
  "language_hint": "es"
}'''
    },
    {
        "nombre": "3. Ordenamiento Burbuja",
        "descripcion": "Algoritmo completo de ordenamiento",
        "json": '''{
  "text": "procedimiento OrdenamientoBurbuja(A[1..n])\\nbegin\\n    i, j, temp\\n    \\n    for i 🡨 1 to n-1 do\\n    begin\\n        for j 🡨 1 to n-i do\\n        begin\\n            if A[j] > A[j+1] then\\n            begin\\n                temp 🡨 A[j]\\n                A[j] 🡨 A[j+1]\\n                A[j+1] 🡨 temp\\n            end\\n        end\\n    end\\nend",
  "language_hint": "es"
}'''
    },
    {
        "nombre": "4. Código con Error (Falta END)",
        "descripcion": "Procedimiento incompleto - falta 'end' final",
        "json": '''{
  "text": "procedimiento Test(n)\\nbegin\\n    x 🡨 5\\n    if x > 0 then\\n    begin\\n        x 🡨 x + 1\\n    end",
  "language_hint": "es"
}'''
    },
    {
        "nombre": "5. Código con Normalizaciones",
        "descripcion": "Usa <= y >= que se normalizarán",
        "json": '''{
  "text": "procedimiento Comparar(x, y)\\nbegin\\n    if x <= y then\\n    begin\\n        mayor 🡨 y\\n    end\\n    if x >= y then\\n    begin\\n        mayor 🡨 x\\n    end\\nend",
  "language_hint": "es"
}'''
    },
    {
        "nombre": "6. Búsqueda Binaria",
        "descripcion": "Algoritmo de búsqueda con while",
        "json": '''{
  "text": "procedimiento BusquedaBinaria(A[1..n], valor)\\nbegin\\n    inicio 🡨 1\\n    fin 🡨 n\\n    \\n    while inicio <= fin do\\n    begin\\n        medio 🡨 └(inicio + fin) / 2┘\\n        \\n        if A[medio] = valor then\\n        begin\\n            return medio\\n        end\\n        else\\n        begin\\n            if A[medio] < valor then\\n            begin\\n                inicio 🡨 medio + 1\\n            end\\n            else\\n            begin\\n                fin 🡨 medio - 1\\n            end\\n        end\\n    end\\n    \\n    return -1\\nend",
  "language_hint": "es"
}'''
    },
    {
        "nombre": "7. Factorial Recursivo",
        "descripcion": "Ejemplo de recursión",
        "json": '''{
  "text": "procedimiento Factorial(n)\\nbegin\\n    if n <= 1 then\\n    begin\\n        return 1\\n    end\\n    else\\n    begin\\n        return n * Factorial(n-1)\\n    end\\nend",
  "language_hint": "es"
}'''
    },
    {
        "nombre": "8. For Loop Simple",
        "descripcion": "Ciclo for básico",
        "json": '''{
  "text": "for i 🡨 1 to 10 do\\nbegin\\n    x 🡨 x + i\\nend",
  "language_hint": "es"
}'''
    },
    {
        "nombre": "9. While Loop",
        "descripcion": "Ciclo while básico",
        "json": '''{
  "text": "while x > 0 do\\nbegin\\n    x 🡨 x - 1\\nend",
  "language_hint": "es"
}'''
    },
    {
        "nombre": "10. If-Else Anidado",
        "descripcion": "Condicionales anidados",
        "json": '''{
  "text": "if x > 10 then\\nbegin\\n    y 🡨 1\\nend\\nelse\\nbegin\\n    if x > 5 then\\n    begin\\n        y 🡨 2\\n    end\\n    else\\n    begin\\n        y 🡨 3\\n    end\\nend",
  "language_hint": "es"
}'''
    }
]

# Mostrar todos los ejemplos
for i, ejemplo in enumerate(ejemplos, 1):
    print(f"\n{'─'*70}")
    print(f"📌 EJEMPLO {i}: {ejemplo['nombre']}")
    print(f"📝 {ejemplo['descripcion']}")
    print(f"\n💾 JSON para copiar:\n")
    print(ejemplo['json'])

print("\n" + "="*70)
print("📋 INSTRUCCIONES:")
print("="*70)
print("""
1. Inicia el servidor:
   python main.py

2. Abre Swagger en tu navegador:
   http://localhost:8000/docs

3. Busca el endpoint:
   POST /api/v1/validate-syntax

4. Click en "Try it out"

5. Copia uno de los JSON de arriba y pégalo en el campo "Request body"

6. Click en "Execute"

7. ¡Mira los resultados! ✨
""")

# Crear un archivo con ejemplos adicionales para testing
print("="*70)
print("💾 GUARDANDO EJEMPLOS EN ARCHIVO...")
print("="*70)

import json

ejemplos_para_archivo = []
for ejemplo in ejemplos:
    # Convertir el string JSON a dict
    ejemplo_dict = json.loads(ejemplo['json'])
    ejemplos_para_archivo.append({
        "nombre": ejemplo['nombre'],
        "descripcion": ejemplo['descripcion'],
        "request": ejemplo_dict
    })

# Guardar en archivo
with open("ejemplos_swagger.json", "w", encoding="utf-8") as f:
    json.dump(ejemplos_para_archivo, f, indent=2, ensure_ascii=False)

print(f"\n✅ Se guardaron {len(ejemplos)} ejemplos en 'ejemplos_swagger.json'")
print("\nTambién puedes usar estos ejemplos con curl:")
print("\ncurl -X POST http://localhost:8000/api/v1/validate-syntax \\")
print('  -H "Content-Type: application/json" \\')
print('  -d \'{"text": "x 🡨 5", "language_hint": "es"}\'')

print("\n" + "="*70)
print("🎉 ¡LISTO PARA USAR EN SWAGGER!")
print("="*70 + "\n")
