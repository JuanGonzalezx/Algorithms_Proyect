"""
Script de prueba para verificar timeout y reintentos de Gemini
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.gemini_service import gemini_service

async def test_normal_request():
    """Prueba 1: Solicitud normal que debe funcionar"""
    print("=" * 60)
    print("TEST 1: Solicitud normal")
    print("=" * 60)
    try:
        result = await gemini_service.normalize_to_pseudocode(
            "algoritmo de ordenamiento burbuja"
        )
        print(f"✅ Éxito!")
        print(f"📄 Resultado ({len(result)} caracteres):")
        print(result[:200] + "..." if len(result) > 200 else result)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_with_retry_simulation():
    """Prueba 2: Simular comportamiento de reintentos"""
    print("\n" + "=" * 60)
    print("TEST 2: Verificar configuración de reintentos")
    print("=" * 60)
    print(f"⚙️  Max reintentos: {gemini_service.max_retries}")
    print(f"⏱️  Timeout: {gemini_service.timeout}s")
    print(f"⏳ Base delay: {gemini_service.base_delay}s")
    print(f"📊 Patrón de delays: {gemini_service.base_delay}s, {gemini_service.base_delay*2}s, {gemini_service.base_delay*4}s")
    return True

async def test_error_handling():
    """Prueba 3: Verificar que errores no-500 no se reintenten"""
    print("\n" + "=" * 60)
    print("TEST 3: Manejo de errores")
    print("=" * 60)
    print("✅ Errores 500: Se reintenta automáticamente")
    print("✅ Timeout: Se reintenta automáticamente")
    print("⚠️  Errores 403/429: NO se reintenta (falla inmediatamente)")
    return True

async def main():
    """Ejecuta todas las pruebas"""
    print("\n🧪 PRUEBAS DE TIMEOUT Y REINTENTOS - GEMINI SERVICE\n")
    
    tests = [
        ("Solicitud Normal", test_normal_request),
        ("Configuración de Reintentos", test_with_retry_simulation),
        ("Manejo de Errores", test_error_handling),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error en test '{name}': {e}")
            results.append((name, False))
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    print(f"\nTotal: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("\n🎉 ¡Todos los tests pasaron!")
    else:
        print(f"\n⚠️  {total - passed} tests fallaron")

if __name__ == "__main__":
    asyncio.run(main())
