"""
Script de prueba para el endpoint /api/v1/analyze (análisis completo)
"""
import requests
import json

# URL del endpoint
BASE_URL = "http://localhost:8000"
ENDPOINT = f"{BASE_URL}/api/v1/analyze"

# Código de ejemplo 1: Bubble Sort (pseudocódigo)
codigo_bubble_sort = """
procedimiento burbuja(A, n)
begin
    for i 🡨 1 to n - 1 do
    begin
        for j 🡨 1 to n - i do
        begin
            if A[j] > A[j + 1] then
            begin
                temp 🡨 A[j]
                A[j] 🡨 A[j + 1]
                A[j + 1] 🡨 temp
            end
        end
    end
end
"""

# Código de ejemplo 2: Lenguaje natural
lenguaje_natural_ejemplo = """
Quiero un algoritmo que ordene un arreglo usando el método de burbuja.
El algoritmo debe comparar elementos adyacentes e intercambiarlos si están en el orden incorrecto.
Este proceso se repite hasta que el arreglo esté completamente ordenado.
"""

def test_analyze_endpoint(use_natural_language=False):
    """
    Prueba el endpoint /api/v1/analyze.
    
    Args:
        use_natural_language: Si True, usa lenguaje natural; si False, usa pseudocódigo
    """
    
    print("=" * 80)
    print("PRUEBA DEL ENDPOINT /api/v1/analyze")
    print("=" * 80)
    print()
    
    # Seleccionar el código según el modo
    if use_natural_language:
        codigo_a_usar = lenguaje_natural_ejemplo.strip()
        tipo = "LENGUAJE NATURAL"
    else:
        codigo_a_usar = codigo_bubble_sort.strip()
        tipo = "PSEUDOCÓDIGO"
    
    print(f"Modo de prueba: {tipo}")
    print()
    
    # Preparar payload
    payload = {
        "text": codigo_a_usar,
        "language_hint": "es"
    }
    
    print("📤 Enviando petición...")
    print(f"   Endpoint: {ENDPOINT}")
    print(f"   Longitud del código: {len(payload['text'])} caracteres")
    print()
    
    try:
        # Hacer la petición
        response = requests.post(
            ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Respuesta recibida: HTTP {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ ANÁLISIS EXITOSO")
            print("=" * 80)
            print()
            
            # 1. Validación
            print("1️⃣ VALIDACIÓN SINTÁCTICA:")
            print("-" * 80)
            validation = data.get("validation", {})
            print(f"   ✓ Válido: {validation.get('era_algoritmo_valido', False)}")
            print(f"   ✓ Errores: {len(validation.get('errores', []))}")
            print(f"   ✓ Normalizaciones: {len(validation.get('normalizaciones', []))}")
            print()
            
            # 2. AST
            print("2️⃣ AST (Abstract Syntax Tree):")
            print("-" * 80)
            ast_data = data.get("ast", {})
            metadata = ast_data.get("metadata", {})
            print(f"   ✓ Éxito: {ast_data.get('success', False)}")
            print(f"   ✓ Funciones: {metadata.get('functions', 0)}")
            print(f"   ✓ Nodos totales: {metadata.get('total_nodes', 0)}")
            print()
            
            # 3. Costos
            print("3️⃣ ANÁLISIS DE COSTOS (Sumatorias):")
            print("-" * 80)
            costs = data.get("costs", {})
            total_cost = costs.get("total", {})
            print(f"   ✓ Nodos analizados: {len(costs.get('per_node', []))}")
            print()
            print("   Costos totales (sin resolver):")
            print(f"   • Best:  {total_cost.get('best', 'N/A')}")
            print(f"   • Avg:   {total_cost.get('avg', 'N/A')}")
            print(f"   • Worst: {total_cost.get('worst', 'N/A')}")
            print()
            
            # 4. Solución
            print("4️⃣ SOLUCIÓN (Sumatorias resueltas):")
            print("-" * 80)
            solution = data.get("solution", {})
            exact = solution.get("exact", {})
            big_o = solution.get("big_o", {})
            bounds = solution.get("bounds", {})
            
            print("   Expresiones exactas:")
            print(f"   • Best:  {exact.get('best', 'N/A')}")
            print(f"   • Avg:   {exact.get('avg', 'N/A')}")
            print(f"   • Worst: {exact.get('worst', 'N/A')}")
            print()
            
            print("   Big-O (término dominante):")
            print(f"   • Best:  {big_o.get('best', 'N/A')}")
            print(f"   • Avg:   {big_o.get('avg', 'N/A')}")
            print(f"   • Worst: {big_o.get('worst', 'N/A')}")
            print()
            
            print("   Cotas asintóticas:")
            print(f"   • Ω (omega): {bounds.get('omega', 'N/A')}")
            print(f"   • Θ (theta): {bounds.get('theta', 'N/A')}")
            print(f"   • O (big-o): {bounds.get('big_o', 'N/A')}")
            print()
            
            # Metadatos
            print("📊 METADATOS:")
            print("-" * 80)
            metadata_analysis = data.get("metadata", {})
            for key, value in metadata_analysis.items():
                if key == "final_pseudocode" and value and len(str(value)) > 100:
                    print(f"   • {key}: (ver archivo JSON)")
                else:
                    print(f"   • {key}: {value}")
            print()
            
            # Mostrar pseudocódigo final si se usó normalización
            if metadata_analysis.get("used_gemini_normalization"):
                print("📝 PSEUDOCÓDIGO GENERADO (Gemini):")
                print("-" * 80)
                final_pseudo = metadata_analysis.get("final_pseudocode", "N/A")
                print(final_pseudo[:500] + ("..." if len(final_pseudo) > 500 else ""))
                print()
            
            # Guardar respuesta completa en archivo JSON
            with open("test_complete_response.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print("💾 Respuesta completa guardada en: test_complete_response.json")
            print()
            
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(response.text)
        
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo:")
        print("   python -m uvicorn main:app --reload --port 8000")
    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    import sys
    
    # Permitir elegir el modo desde la línea de comandos
    use_natural = "--natural" in sys.argv or "-n" in sys.argv
    
    if use_natural:
        print("\n🗣️  Probando con LENGUAJE NATURAL\n")
    else:
        print("\n📝 Probando con PSEUDOCÓDIGO\n")
    
    test_analyze_endpoint(use_natural_language=use_natural)
