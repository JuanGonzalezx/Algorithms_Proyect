"""
Test que replica EXACTAMENTE el flujo del endpoint /api/v1/analyze
para encontrar dónde falla con lenguaje natural
"""
import asyncio
import sys
from app.services.gemini_service import gemini_service

async def test_normalize_flow():
    print("=" * 80)
    print("🧪 TEST: Replicando flujo completo del endpoint /analyze")
    print("=" * 80)
    
    # Input de prueba (lenguaje natural)
    input_text = "Ordena un arreglo usando el algoritmo de burbuja"
    
    print(f"\n📝 Input: {input_text}")
    print(f"\n📊 Estado de Gemini Service:")
    print(f"   - Keys cargadas: {len(gemini_service.api_keys)}")
    print(f"   - Key activa: ****{gemini_service.api_keys[gemini_service.current_key_index][-4:]}")
    print(f"   - Modelo: {gemini_service.model._model_name if hasattr(gemini_service.model, '_model_name') else 'unknown'}")
    
    try:
        print("\n" + "=" * 80)
        print("PASO 1: Llamando a normalize_to_pseudocode()")
        print("=" * 80)
        
        normalized_pseudocode = await gemini_service.normalize_to_pseudocode(input_text)
        
        print("\n✅ ÉXITO! Pseudocódigo generado:")
        print("=" * 80)
        print(normalized_pseudocode)
        print("=" * 80)
        print(f"\nLongitud: {len(normalized_pseudocode)} caracteres")
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERROR EN normalize_to_pseudocode()")
        print("=" * 80)
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        print("\nTraceback completo:")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        
        # Verificar si es error 429
        error_str = str(e)
        if "429" in error_str or "quota" in error_str.lower():
            print("\n⚠️  DIAGNÓSTICO: Error 429 - Cuota excedida")
            print("   La API key ha alcanzado su límite de 50 requests/día")
            print("   Solución: Agregar más keys al .env")
        elif "503" in error_str:
            print("\n⚠️  DIAGNÓSTICO: Error 503 - Servicio no disponible")
            print("   El modelo puede no existir o estar temporalmente no disponible")
        
        return

if __name__ == "__main__":
    asyncio.run(test_normalize_flow())
