"""
Test directo de Gemini para verificar que la API key funciona
"""
import asyncio
import sys
from app.services.gemini_service import gemini_service

async def test_gemini():
    print("🧪 Probando conexión directa con Gemini...")
    print(f"📊 Keys cargadas: {len(gemini_service.api_keys)}")
    print(f"🔑 Key activa: ****{gemini_service.api_keys[0][-4:]}")
    
    try:
        prompt = """
        Convierte este código a pseudocódigo estándar:
        
        Para i desde 1 hasta 5:
            Imprimir i
        """
        
        print("\n📤 Enviando petición a Gemini...")
        result = await gemini_service._generate_content(prompt)
        print("\n✅ Respuesta recibida:")
        print(result[:200] + "..." if len(result) > 200 else result)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini())
