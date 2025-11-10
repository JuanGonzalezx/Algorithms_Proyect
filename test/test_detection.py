"""
Test simple del endpoint /analyze (sin servidor HTTP)
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api.routes import _detect_natural_language

# Ejemplos de prueba
tests = [
    ("procedimiento burbuja(A, n)\nbegin\n  for i <- 1 to n do", False, "Pseudocódigo con palabras clave"),
    ("Quiero un algoritmo que ordene un arreglo", True, "Lenguaje natural descriptivo"),
    ("implementa bubble sort que ordena elementos", True, "Lenguaje natural imperativo"),
    ("function sort(arr) begin return arr end", False, "Pseudocódigo con function/begin/end"),
    ("Dame un programa para buscar el máximo", True, "Solicitud en lenguaje natural"),
]

print("=" * 80)
print("PRUEBA DE DETECCIÓN: Lenguaje Natural vs Pseudocódigo")
print("=" * 80)
print()

for i, (texto, esperado, descripcion) in enumerate(tests, 1):
    resultado = _detect_natural_language(texto)
    status = "✅" if resultado == esperado else "❌"
    
    print(f"{status} Test {i}: {descripcion}")
    print(f"   Texto: \"{texto[:60]}...\"" if len(texto) > 60 else f"   Texto: \"{texto}\"")
    print(f"   Esperado: {'Natural' if esperado else 'Pseudocódigo'}")
    print(f"   Resultado: {'Natural' if resultado else 'Pseudocódigo'}")
    print()

print("=" * 80)
