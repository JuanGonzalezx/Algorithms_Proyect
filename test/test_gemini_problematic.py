"""
Test del servicio Gemini con el prompt problemático
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.gemini_service import gemini_service

async def test_problematic_prompt():
    """Prueba con el prompt que causó el error"""
    prompt = "Algoritmo que compara elementos adyacentes y los intercambia si están en orden incorrecto hasta que no se necesiten más intercambios."
    
    print("=" * 70)
    print("TEST: Prompt Problemático de Burbuja")
    print("=" * 70)
    print(f"\n📝 Prompt:\n{prompt}\n")
    
    try:
        result = await gemini_service.normalize_to_pseudocode(prompt)
        
        print("=" * 70)
        print("✅ RESULTADO GENERADO:")
        print("=" * 70)
        print(result)
        print("=" * 70)
        
        # Verificar que contiene las palabras clave necesarias
        checks = {
            "begin": "begin" in result.lower(),
            "end": "end" in result.lower(),
            "repeat o for o while": any(word in result.lower() for word in ["repeat", "for", "while"]),
        }
        
        print("\n🔍 VERIFICACIONES:")
        for check_name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}")
        
        all_passed = all(checks.values())
        
        if all_passed:
            print("\n✅ El pseudocódigo parece válido")
        else:
            print("\n⚠️ El pseudocódigo puede tener problemas")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

async def test_multiple_descriptions():
    """Prueba con múltiples descripciones"""
    descriptions = [
        "ordenamiento burbuja",
        "algoritmo de búsqueda binaria",
        "algoritmo que compara elementos adyacentes",
    ]
    
    print("\n" + "=" * 70)
    print("TEST MÚLTIPLE: Varias Descripciones")
    print("=" * 70)
    
    results = []
    for i, desc in enumerate(descriptions, 1):
        print(f"\n[{i}/{len(descriptions)}] {desc}")
        try:
            result = await gemini_service.normalize_to_pseudocode(desc)
            print(f"  ✅ Generado ({len(result)} caracteres)")
            results.append((desc, True, len(result)))
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append((desc, False, 0))
    
    print("\n" + "=" * 70)
    print("RESUMEN:")
    print("=" * 70)
    for desc, success, length in results:
        status = "✅" if success else "❌"
        print(f"{status} {desc[:50]:50s} - {length:4d} chars")
    
    success_count = sum(1 for _, success, _ in results if success)
    print(f"\nTotal: {success_count}/{len(results)} exitosos")

async def main():
    print("🧪 TEST DEL SERVICIO GEMINI - PROMPT PROBLEMÁTICO\n")
    
    # Test principal
    result = await test_problematic_prompt()
    
    # Tests adicionales
    await test_multiple_descriptions()
    
    print("\n" + "=" * 70)
    print("FIN DE TESTS")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
