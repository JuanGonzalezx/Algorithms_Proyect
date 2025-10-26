"""Script para probar el endpoint /ast"""
import requests
import json

# Test 1: Código simple con for
print("=" * 60)
print("TEST 1: Código simple con for loop")
print("=" * 60)

code1 = """def f(n):
  s=0
  for i in range(1,n):
    s+=i
  return s"""

response1 = requests.post(
    "http://localhost:8000/api/v1/ast",
    json={"content": code1, "from_lang": "python"}
)

print(f"Status: {response1.status_code}")
if response1.status_code == 200:
    ast_data = response1.json()
    print(f"Function name: {ast_data['ast']['functions'][0]['name']}")
    print(f"Params: {[p['name'] for p in ast_data['ast']['functions'][0]['params']]}")
    print(f"For loop variable: {ast_data['ast']['functions'][0]['body']['statements'][1]['var']}")
    print("✅ Test 1 PASSED")
else:
    print(f"❌ Error: {response1.text}")

# Test 2: Sintaxis no soportada (range con step)
print("\n" + "=" * 60)
print("TEST 2: Range con step (debe fallar con 400)")
print("=" * 60)

code2 = """def test():
  for i in range(1, 10, 2):
    pass"""

response2 = requests.post(
    "http://localhost:8000/api/v1/ast",
    json={"content": code2, "from_lang": "python"}
)

print(f"Status: {response2.status_code}")
if response2.status_code == 400 and "unsupported_syntax" in response2.text:
    print("✅ Test 2 PASSED - Correctamente rechazó sintaxis no soportada")
else:
    print(f"❌ Test 2 FAILED: {response2.text}")

# Test 3: from_lang inválido
print("\n" + "=" * 60)
print("TEST 3: from_lang inválido (debe fallar con 400)")
print("=" * 60)

response3 = requests.post(
    "http://localhost:8000/api/v1/ast",
    json={"content": "def test(): pass", "from_lang": "javascript"}
)

print(f"Status: {response3.status_code}")
if response3.status_code == 400:
    print("✅ Test 3 PASSED - Correctamente rechazó from_lang='javascript'")
else:
    print(f"❌ Test 3 FAILED: {response3.text}")

print("\n" + "=" * 60)
print("RESUMEN: Todos los tests completados")
print("=" * 60)
