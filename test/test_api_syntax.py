"""
Script de ejemplo para probar el API del agente de validación sintáctica.
"""
import requests
import json


def test_api():
    """Prueba el API de validación sintáctica."""
    
    base_url = "http://localhost:8000"
    
    # 1. Health check
    print("\n" + "="*60)
    print("1. Health Check")
    print("="*60)
    
    response = requests.get(f"{base_url}/api/v1/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # 2. Validar código válido
    print("\n" + "="*60)
    print("2. Validación de código válido")
    print("="*60)
    
    valid_code = """
procedimiento OrdenarBurbuja(A[1..n])
begin
    i, j, temp
    for i 🡨 1 to n-1 do
    begin
        for j 🡨 1 to n-i do
        begin
            if A[j] > A[j+1] then
            begin
                temp 🡨 A[j]
                A[j] 🡨 A[j+1]
                A[j+1] 🡨 temp
            end
        end
    end
end
"""
    
    payload = {
        "text": valid_code,
        "language_hint": "es"
    }
    
    response = requests.post(
        f"{base_url}/api/v1/validate-syntax",
        json=payload
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Válido: {result['era_algoritmo_valido']}")
    print(f"Errores: {len(result['errores'])}")
    print(f"Normalizaciones: {len(result['normalizaciones'])}")
    
    # 3. Validar código con errores
    print("\n" + "="*60)
    print("3. Validación de código con errores")
    print("="*60)
    
    invalid_code = """
procedimiento Ejemplo(n)
begin
    x 🡨 5
    if x > 0 then
    begin
        x 🡨 x + 1
    end
"""  # Falta 'end' final
    
    payload = {
        "text": invalid_code,
        "language_hint": "es"
    }
    
    response = requests.post(
        f"{base_url}/api/v1/validate-syntax",
        json=payload
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Válido: {result['era_algoritmo_valido']}")
    print(f"Errores encontrados: {len(result['errores'])}")
    if result['errores']:
        print("\nDetalles del error:")
        for error in result['errores']:
            print(f"  - Línea {error['linea']}, Columna {error['columna']}")
            print(f"    Sugerencia: {error['sugerencia']}")
    
    # 4. Código con normalizaciones
    print("\n" + "="*60)
    print("4. Código con normalizaciones")
    print("="*60)
    
    code_with_normalizations = """procedimiento Test(n)
begin
    x 🡨 5
    if x <= 10 then
    begin
        y 🡨 x + 1
    end
end"""
    
    payload = {
        "text": code_with_normalizations,
        "language_hint": "es"
    }
    
    response = requests.post(
        f"{base_url}/api/v1/validate-syntax",
        json=payload
    )
    result = response.json()
    print(f"Válido: {result['era_algoritmo_valido']}")
    print(f"Normalizaciones aplicadas:")
    for norm in result['normalizaciones']:
        print(f"  - {norm}")
    
    print("\n" + "="*60)
    print("✅ Todas las pruebas completadas")
    print("="*60)


if __name__ == "__main__":
    print("\n🌐 PRUEBAS DEL API - VALIDACIÓN SINTÁCTICA\n")
    print("⚠️  Asegúrate de que el servidor esté corriendo:")
    print("   python main.py")
    print()
    
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar al servidor")
        print("   Ejecuta primero: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
