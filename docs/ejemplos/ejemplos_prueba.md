# Ejemplos de Pseudocódigo para Pruebas

## Ejemplo 1: Factorial (Recursivo)
```
factorial(n)
begin
    if (n ≤ 1) then
    begin
        return 1
    end
    else
    begin
        return n * CALL factorial(n - 1)
    end
end
```

## Ejemplo 2: Suma de array (Iterativo)
```
suma_array(A, n)
begin
    suma 🡨 0
    for i 🡨 1 to n do
    begin
        suma 🡨 suma + A[i]
    end
    return suma
end
```

## Ejemplo 3: Búsqueda lineal
```
busqueda_lineal(A, n, x)
begin
    for i 🡨 1 to n do
    begin
        if (A[i] = x) then
        begin
            return i
        end
    end
    return -1
end
```

## Ejemplo 4: Fibonacci (Recursivo)
```
fibonacci(n)
begin
    if (n ≤ 1) then
    begin
        return n
    end
    else
    begin
        return CALL fibonacci(n - 1) + CALL fibonacci(n - 2)
    end
end
```

## Ejemplos en Lenguaje Natural

1. "Crea un algoritmo que calcule el factorial de un número"
2. "Implementa un algoritmo que sume todos los elementos de un array"
3. "Diseña un algoritmo de búsqueda que encuentre un elemento en una lista"
4. "Crea un algoritmo que ordene una lista de números de menor a mayor"