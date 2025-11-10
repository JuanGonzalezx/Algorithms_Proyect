"""
Test completo del endpoint /api/v1/analyze con lenguaje natural
"""
import requests
import json

# URL del endpoint
url = "http://localhost:8000/api/v1/analyze"

# Payload con lenguaje natural
payload = {
    "text": "Ordena un arreglo usando el algoritmo de burbuja"
}

print("=" * 80)
print("🧪 PROBANDO ENDPOINT /api/v1/analyze")
print("=" * 80)
print(f"\n📤 Enviando petición a: {url}")
print(f"📝 Payload: {json.dumps(payload, indent=2)}")
print("\n⏳ Esperando respuesta...\n")

try:
    response = requests.post(url, json=payload, timeout=120)
    
    print(f"📊 Status Code: {response.status_code}")
    print(f"📋 Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("\n✅ ÉXITO! Respuesta recibida:")
        print("=" * 80)
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("=" * 80)
    else:
        print(f"\n❌ ERROR {response.status_code}")
        print("=" * 80)
        print("Respuesta completa:")
        print(response.text)
        print("=" * 80)
        
except requests.exceptions.Timeout:
    print("❌ TIMEOUT - La petición tardó más de 120 segundos")
except requests.exceptions.ConnectionError:
    print("❌ CONNECTION ERROR - No se pudo conectar al servidor")
    print("Asegúrate de que el servidor esté corriendo: uvicorn main:app --reload")
except Exception as e:
    print(f"❌ ERROR INESPERADO: {type(e).__name__}")
    print(f"Mensaje: {str(e)}")
    import traceback
    traceback.print_exc()
