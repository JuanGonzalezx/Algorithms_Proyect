#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testear costos por línea con formato simple (ejemplo de Selection Sort)
"""

import sys
from app.modules.syntax_validator.agent import get_syntax_validator
from app.modules.parser.service import get_parser_agent
from app.modules.analyzer.cost_model import CostAnalyzerAgent
from app.modules.solver.solver import get_series_solver
from app.shared.models import PseudocodeIn

def main():
    # Selection Sort - similar al ejemplo del usuario
    pseudocode = """
procedimiento SelectionSort(A, n)
begin
    for i 🡨 1 to n - 1 do
    begin
        min_index 🡨 i
        for j 🡨 i + 1 to n do
        begin
            if A[j] < A[min_index] then
            begin
                min_index 🡨 j
            end
        end
        if min_index != i then
        begin
            temp 🡨 A[i]
            A[i] 🡨 A[min_index]
            A[min_index] 🡨 temp
        end
    end
end
"""

    print("=" * 80)
    print("TEST: COSTOS POR LINEA (Selection Sort)")
    print("=" * 80)
    print()
    
    try:
        # 1. Validar sintaxis
        validator = get_syntax_validator()
        validation = validator.validate(PseudocodeIn(text=pseudocode))
        
        if not validation.era_algoritmo_valido:
            print("[ERROR] Código inválido")
            for err in validation.errores:
                print(f"  - {err.detalle}")
            return 1
        
        # 2. Parsear
        parser = get_parser_agent()
        ast = parser.parse(validation.codigo_corregido)
        
        # 3. Analizar costos
        analyzer = CostAnalyzerAgent()
        costs_result = analyzer.analyze(ast, validation.codigo_corregido)
        
        # 4. Resolver sumatorias
        solver = get_series_solver()
        solution_result = solver.solve(costs_result.total)
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print(f"Total nodos: {len(costs_result.per_node)}")
    print(f"Total lineas con costos: {len(costs_result.per_line)}")
    print()
    
    # Mostrar costos por línea (formato simple)
    print("=" * 80)
    print("COSTOS POR LINEA")
    print("=" * 80)
    print()
    
    for lc in costs_result.per_line:
        # Mostrar solo worst case para simplificar
        print(f"Linea {lc.line_number:2d}: {lc.code}")
        print(f"  => C{lc.line_number} * {lc.cost.worst}")
        print()
    
    # Mostrar resultado resuelto
    print("=" * 80)
    print("RESULTADO FINAL (Total del programa)")
    print("=" * 80)
    print()
    print(f"Exact (Best):  {solution_result.exact.best}")
    print(f"Exact (Avg):   {solution_result.exact.avg}")
    print(f"Exact (Worst): {solution_result.exact.worst}")
    print()
    print(f"Big-O: {solution_result.big_o.worst}")
    print()
    
    print("[OK] Test exitoso!")
    print()
    print("Nota: Los costos por linea muestran C_i * frecuencia_ejecucion")
    print("      Donde frecuencia_ejecucion se expresa como Sum(...)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
