# Prompt:
# Crea una función que ordene una lista de números usando el algoritmo de burbuja

def ordenamiento_burbuja(lista):
    """Ordena una lista de números usando el algoritmo de burbuja."""
    n = len(lista)
    # Recorrer todos los elementos de la lista
    for i in range(n):
        # El último i elementos ya están en su lugar
        for j in range(0, n - i - 1):
            # Recorrer la lista de 0 a n-i-1
            # Intercambiar si el elemento encontrado es mayor
            # que el siguiente elemento
            if lista[j] > lista[j + 1]:
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
    return lista