"""
Script de diagnóstico para verificar el servicio de Gemini
"""
import google.generativeai as genai
from decouple import config

def test_gemini_connection():
    """Prueba la conexión con Gemini API"""
    api_key = config('GEMINI_API_KEY')
    print(f"🔑 API Key configurada: {api_key[:10]}...{api_key[-4:]}")
    
    # Configurar API
    genai.configure(api_key=api_key)
    
    # Listar modelos disponibles
    print("\n📋 Modelos disponibles:")
    try:
        models = genai.list_models()
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"  ✓ {model.name}")
    except Exception as e:
        print(f"  ❌ Error al listar modelos: {e}")
        return False
    
    # Intentar con diferentes versiones del modelo
    model_names = [
        "gemini-2.5-pro",      # Actual
        "gemini-2.0-flash",     # Alternativa más reciente
        "gemini-1.5-pro",      # Versión estable
        "gemini-1.5-flash",    # Versión rápida
        "gemini-pro",          # Versión base
    ]
    
    test_prompt = "Di solo 'OK' si funciono"
    
    print("\n🧪 Probando modelos:")
    for model_name in model_names:
        try:
            print(f"\n  Probando {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(test_prompt)
            print(f"    ✅ {model_name}: {response.text.strip()}")
            return model_name  # Retorna el primer modelo que funcione
        except Exception as e:
            error_msg = str(e)
            if "500" in error_msg:
                print(f"    ❌ {model_name}: Error 500 (modelo no disponible o error interno)")
            elif "404" in error_msg:
                print(f"    ⚠️ {model_name}: Modelo no encontrado")
            elif "403" in error_msg:
                print(f"    🔒 {model_name}: Sin permisos (API Key inválida)")
            elif "429" in error_msg:
                print(f"    ⏱️ {model_name}: Límite de cuota excedido")
            else:
                print(f"    ❌ {model_name}: {error_msg}")
    
    print("\n❌ Ningún modelo funciona correctamente")
    return None

if __name__ == "__main__":
    print("🚀 Diagnóstico de Gemini API\n")
    working_model = test_gemini_connection()
    
    if working_model:
        print(f"\n✅ Recomendación: Usar modelo '{working_model}'")
        print(f"\n💡 Actualiza gemini_service.py línea 20:")
        print(f'   self.model = genai.GenerativeModel("{working_model}")')
    else:
        print("\n❌ Verifica:")
        print("   1. API Key válida en .env")
        print("   2. Cuota disponible en Google AI Studio")
        print("   3. Conexión a internet")
        print("   4. Visita: https://makersuite.google.com/app/apikey")
