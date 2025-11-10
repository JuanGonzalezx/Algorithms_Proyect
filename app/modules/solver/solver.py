"""
Series Solver: resuelve sumatorias simbólicas y calcula cotas asintóticas.

Este módulo toma expresiones de costo con notación Sum() y las simplifica usando SymPy,
luego calcula las cotas asintóticas (Ω, Θ, O).
"""
import re
from typing import Dict, Optional
import sympy as sp
from sympy import symbols, Sum, simplify, sympify, Poly, oo
from sympy.series import Order

from app.shared.models import CostExpr, ExactCosts, AsymptoticBounds, SolveOut


class SeriesSolver:
    """
    Resuelve expresiones de costo simbólicas y calcula cotas asintóticas.
    
    Flujo:
    1. Parse: Convierte strings como "Sum(1, (k, 1, n))" a expresiones SymPy
    2. Solve: Resuelve sumatorias usando .doit()
    3. Simplify: Simplifica algebraicamente
    4. Asymptotic: Calcula Ω, Θ, O
    """
    
    def __init__(self):
        """Inicializa el solver con símbolos comunes."""
        # Símbolos comunes para variables de control
        self.n = symbols('n', positive=True, integer=True)
        self.i = symbols('i', positive=True, integer=True)
        self.j = symbols('j', positive=True, integer=True)
        self.k = symbols('k', positive=True, integer=True)
        self.m = symbols('m', positive=True, integer=True)
        
        # Cache para símbolos desconocidos
        self._unknown_symbols: Dict[str, sp.Symbol] = {}
    
    def _fix_nested_sums(self, expr_str: str) -> str:
        """
        Arregla variables de índice en sumatorias anidadas.
        
        El problem es que cost_analyzer genera: Sum(Sum(..., (k, 1, n-i)), (k, 1, n-1))
        donde ambas sumas usan 'k', pero sympify los trata como la misma variable.
        
        Esta función NO está siendo el problema real. El problema es que sympify
        parsea Sum con múltiples rangos como sumas múltiples en paralelo.
        
        Args:
            expr_str: Expresión con posibles sumatorias anidadas
            
        Returns:
            Expresión sin cambios (por ahora)
        """
        # Por ahora, retornar sin cambios
        # El verdadero problema está en cómo sympify interpreta Sum(expr, rango1, rango2)
        return expr_str
    
    def solve(self, cost_expr: CostExpr, show_steps: bool = True, per_line_costs: list = None) -> SolveOut:
        """
        Resuelve un CostExpr completo (best, avg, worst).
        
        Args:
            cost_expr: Expresión de costo con los tres casos (análisis por bloques - NO SE USA)
            show_steps: Si True, genera el proceso paso a paso
            per_line_costs: Lista opcional de LineCost para generar solución línea por línea
            
        Returns:
            SolveOut con expresiones exactas, cotas asintóticas y pasos de resolución
        """
        from app.shared.models import SolutionStep
        
        # NO generar el análisis por bloques (steps), solo el análisis por línea
        steps = []
        
        # Calcular exact desde la suma de TODAS las líneas (incluyendo For/While)
        # Esto asegura que exact coincida con el análisis por línea
        if per_line_costs:
            # Sumar los costos de todas las líneas para cada caso
            best_sum = " + ".join([f"({lc.cost.best})" for lc in per_line_costs])
            avg_sum = " + ".join([f"({lc.cost.avg})" for lc in per_line_costs])
            worst_sum = " + ".join([f"({lc.cost.worst})" for lc in per_line_costs])
            
            # Resolver las sumas
            best_exact, _ = self._solve_expression_with_steps(best_sum, "best", 1)
            avg_exact, _ = self._solve_expression_with_steps(avg_sum, "avg", 1)
            worst_exact, _ = self._solve_expression_with_steps(worst_sum, "worst", 1)
        else:
            # Fallback: usar el análisis por bloques si no hay per_line_costs
            best_exact, _ = self._solve_expression_with_steps(cost_expr.best, "best", 1)
            avg_exact, _ = self._solve_expression_with_steps(cost_expr.avg, "avg", 1)
            worst_exact, _ = self._solve_expression_with_steps(cost_expr.worst, "worst", 1)
        
        # Generar SOLO la solución línea por línea (este es el método solicitado)
        steps_by_line = []
        if per_line_costs and show_steps:
            steps_by_line = self._solve_by_line_with_steps(per_line_costs)
        
        # Calcular Big-O simplificado
        best_big_o = self._extract_big_o(best_exact)
        avg_big_o = self._extract_big_o(avg_exact)
        worst_big_o = self._extract_big_o(worst_exact)
        
        # Calcular cotas asintóticas (Ω, Θ, O)
        bounds = self._calculate_bounds(best_exact, avg_exact, worst_exact)
        
        return SolveOut(
            steps=steps,
            steps_by_line=steps_by_line,
            exact=ExactCosts(
                best=str(best_exact),
                avg=str(avg_exact),
                worst=str(worst_exact)
            ),
            big_o=ExactCosts(
                best=best_big_o,
                avg=avg_big_o,
                worst=worst_big_o
            ),
            bounds=bounds
        )
    
    def _solve_expression(self, expr_str: str) -> sp.Expr:
        """
        Resuelve una expresión individual.
        
        Args:
            expr_str: String con notación Sum() o expresión algebraica
            
        Returns:
            Expresión SymPy simplificada
        """
        if not expr_str or expr_str == "0":
            return sp.Integer(0)
        
        try:
            # Convertir string a expresión SymPy
            expr = self._parse_expression(expr_str)
            
            # Resolver sumatorias
            expr = expr.doit()
            
            # Simplificar
            expr = simplify(expr)
            
            # Convertir decimales a fracciones racionales (1.25 -> 5/4)
            expr = sp.nsimplify(expr, rational=True)
            
            # Intentar factorizar para obtener forma n(n-1)/2 en lugar de n²/2 - n/2
            # Si no se puede factorizar, simplify ya lo dejó en su mejor forma
            try:
                factored = sp.factor(expr)
                # Usar la forma factorizada solo si es más compacta o igual de compacta
                if len(str(factored)) <= len(str(expr)):
                    expr = factored
            except:
                pass  # Si factor falla, mantener la expresión simplificada
            
            return expr
            
        except Exception as e:
            # Si hay error, retornar como símbolo desconocido
            unknown_name = f"unknown({expr_str})"
            if unknown_name not in self._unknown_symbols:
                self._unknown_symbols[unknown_name] = symbols(unknown_name)
            return self._unknown_symbols[unknown_name]
    
    def _solve_expression_with_steps(self, expr_str: str, case: str, start_step: int):
        """
        Resuelve una expresión y genera los pasos intermedios.
        
        Args:
            expr_str: Expresión en formato string
            case: "best", "avg" o "worst"
            start_step: Número de paso inicial
            
        Returns:
            tuple: (expresión_resuelta, lista_de_pasos)
        """
        from app.shared.models import SolutionStep
        
        steps = []
        current_step = start_step
        
        if not expr_str or expr_str == "0":
            return sp.Integer(0), steps
        
        try:
            # Paso 1: Parsear expresión
            expr = self._parse_expression(expr_str)
            
            # Identificar todas las sumatorias en la expresión
            sums = self._find_sums(expr)
            
            if sums:
                # Resolver todas las sumatorias con .doit() primero
                expr_with_sums_resolved = expr.doit()
                
                # Ahora buscar y mostrar paso a paso cómo se resolvieron
                # Agrupar sumatorias únicas (pueden repetirse en la expresión)
                unique_sums = []
                seen_sums = set()
                for sum_expr in sums:
                    sum_str = str(sum_expr)
                    if sum_str not in seen_sums:
                        seen_sums.add(sum_str)
                        unique_sums.append(sum_expr)
                
                # Paso 2: Resolver cada sumatoria única
                for sum_expr in unique_sums:
                    # Si la sumatoria tiene múltiples límites, son sumatorias anidadas aplanadas por SymPy
                    if isinstance(sum_expr, Sum) and len(sum_expr.limits) > 1:
                        # Resolver de adentro hacia afuera (primer límite es el más interno)
                        current_expr = sum_expr.function
                        limits_list = list(sum_expr.limits)
                        
                        for idx, limit in enumerate(limits_list, 1):
                            # Crear sumatoria para este nivel
                            level_sum = Sum(current_expr, limit)
                            solved_level = level_sum.doit()
                            
                            # Descripción según el nivel
                            total_levels = len(limits_list)
                            if total_levels == 2:
                                if idx == 1:
                                    description = f"Resolver sumatoria interna (sobre {limit[0]})"
                                else:
                                    description = f"Resolver sumatoria externa (sobre {limit[0]})"
                            else:
                                if idx == 1:
                                    description = f"Resolver sumatoria más interna (nivel {idx}/{total_levels}, sobre {limit[0]})"
                                elif idx == total_levels:
                                    description = f"Resolver sumatoria más externa (nivel {idx}/{total_levels}, sobre {limit[0]})"
                                else:
                                    description = f"Resolver sumatoria intermedia (nivel {idx}/{total_levels}, sobre {limit[0]})"
                            
                            steps.append(SolutionStep(
                                step_number=current_step,
                                description=description,
                                expression=f"{level_sum} = {solved_level}",
                                case=case
                            ))
                            current_step += 1
                            
                            # La expresión resuelta se convierte en la función del siguiente nivel
                            current_expr = solved_level
                    else:
                        # Sumatoria simple (un solo límite)
                        solved_sum = sum_expr.doit()
                        steps.append(SolutionStep(
                            step_number=current_step,
                            description="Resolver sumatoria",
                            expression=f"{sum_expr} = {solved_sum}",
                            case=case
                        ))
                        current_step += 1
                
                # Mostrar la expresión con todas las sumatorias resueltas
                if str(expr_with_sums_resolved) != str(expr):
                    steps.append(SolutionStep(
                        step_number=current_step,
                        description=f"Sustituir sumatorias resueltas ({case})",
                        expression=f"T(n) = {expr_with_sums_resolved}",
                        case=case
                    ))
                    current_step += 1
                
                expr_after_sums = expr_with_sums_resolved
            else:
                # No hay sumatorias
                expr_after_sums = expr
            
            # Paso 4: Simplificar
            expr_simplified = simplify(expr_after_sums)
            if str(expr_simplified) != str(expr_after_sums):
                steps.append(SolutionStep(
                    step_number=current_step,
                    description=f"Simplificar algebraicamente ({case})",
                    expression=f"T(n) = {expr_simplified}",
                    case=case
                ))
                current_step += 1
            
            # Paso 5: Convertir a fracciones racionales
            expr_rational = sp.nsimplify(expr_simplified, rational=True)
            if str(expr_rational) != str(expr_simplified):
                steps.append(SolutionStep(
                    step_number=current_step,
                    description=f"Convertir a fracciones ({case})",
                    expression=f"T(n) = {expr_rational}",
                    case=case
                ))
                current_step += 1
            
            # Paso 6: Factorizar
            try:
                expr_factored = sp.factor(expr_rational)
                if len(str(expr_factored)) <= len(str(expr_rational)) and str(expr_factored) != str(expr_rational):
                    steps.append(SolutionStep(
                        step_number=current_step,
                        description=f"Factorizar ({case})",
                        expression=f"T(n) = {expr_factored}",
                        case=case
                    ))
                    current_step += 1
                    final_expr = expr_factored
                else:
                    final_expr = expr_rational
            except:
                final_expr = expr_rational
            
            # Paso final: Resultado
            steps.append(SolutionStep(
                step_number=current_step,
                description=f"Resultado final ({case})",
                expression=f"T(n) = {final_expr}",
                case=case
            ))
            
            return final_expr, steps
            
        except Exception as e:
            # Si hay error, retornar como símbolo desconocido
            unknown_name = f"unknown({expr_str})"
            if unknown_name not in self._unknown_symbols:
                self._unknown_symbols[unknown_name] = symbols(unknown_name)
            return self._unknown_symbols[unknown_name], steps
    
    def _solve_by_line_with_steps(self, per_line_costs: list):
        """
        Genera pasos de resolución sumando línea por línea.
        
        Args:
            per_line_costs: Lista de LineCost
            
        Returns:
            Lista de SolutionStep mostrando cómo se suman los costos de cada línea
        """
        from app.shared.models import SolutionStep
        
        steps = []
        step_counter = 1
        
        # Incluir TODAS las líneas para el análisis (incluyendo For/While)
        # Cada línea contribuye con su costo real
        contributing_costs = per_line_costs
        
        if not contributing_costs:
            # No hay líneas, retornar vacío
            return []
        
        # Procesar cada caso (best, avg, worst)
        for case_name, case_attr in [("best", "best"), ("avg", "avg"), ("worst", "worst")]:
            # Paso 1: Mostrar la fórmula general con constantes C1, C2, C3...
            # Usar solo las líneas que contribuyen (no For/While)
            line_costs_str = " + ".join([
                f"C{idx+1}*L{lc.line_number}" for idx, lc in enumerate(contributing_costs)
            ])
            steps.append(SolutionStep(
                step_number=step_counter,
                description=f"Fórmula de costo línea por línea ({case_name})",
                expression=f"T(n) = {line_costs_str}",
                case=case_attr
            ))
            step_counter += 1
            
            # Paso 2: Mostrar cada línea con su costo (sin constante, eso viene después)
            for idx, lc in enumerate(contributing_costs):
                line_cost = getattr(lc.cost, case_attr)
                steps.append(SolutionStep(
                    step_number=step_counter,
                    description=f"Línea {lc.line_number}: {lc.code.strip()[:40]}...",
                    expression=f"L{lc.line_number} = {line_cost}",
                    case=case_attr
                ))
                step_counter += 1
            
            # Paso 3: Sustituir valores (con constantes C1, C2, C3...)
            sum_expression_with_constants = " + ".join([
                f"C{idx+1}*({getattr(lc.cost, case_attr)})" 
                for idx, lc in enumerate(contributing_costs)
            ])
            steps.append(SolutionStep(
                step_number=step_counter,
                description=f"Sustituir valores de cada línea ({case_name})",
                expression=f"T(n) = {sum_expression_with_constants}",
                case=case_attr
            ))
            step_counter += 1
            
            # Paso 4: Factorizar constantes (opcional, para mostrar forma más clara)
            # Sumar solo las expresiones sin constantes para resolver las sumatorias
            sum_expression = " + ".join([
                f"({getattr(lc.cost, case_attr)})" for lc in contributing_costs
            ])
            steps.append(SolutionStep(
                step_number=step_counter,
                description=f"Simplificar (asumiendo C1=C2=...=1 para análisis asintótico) ({case_name})",
                expression=f"T(n) = {sum_expression}",
                case=case_attr
            ))
            step_counter += 1
            
            # Paso 4: Resolver la suma completa CON PASOS INTERMEDIOS
            try:
                # Usar _solve_expression_with_steps para mostrar cada sumatoria resolviéndose
                total_expr, resolution_steps = self._solve_expression_with_steps(
                    sum_expression, 
                    case_attr, 
                    step_counter
                )
                
                # Agregar los pasos de resolución de sumatorias
                steps.extend(resolution_steps)
                step_counter += len(resolution_steps)
                
                # Paso final: mostrar resultado
                steps.append(SolutionStep(
                    step_number=step_counter,
                    description=f"Resultado final línea por línea ({case_name})",
                    expression=f"T(n) = {total_expr}",
                    case=case_attr
                ))
                step_counter += 1
                
            except Exception as e:
                steps.append(SolutionStep(
                    step_number=step_counter,
                    description=f"Error al resolver ({case_name})",
                    expression=f"Error: {str(e)}",
                    case=case_attr
                ))
                step_counter += 1
        
        return steps
    
    def _find_sums(self, expr):
        """
        Encuentra todas las sumatorias en una expresión, ordenadas de más interna a más externa.
        
        Para sumatorias anidadas como Sum(Sum(1, (j, 1, n-i)), (i, 1, n-1)),
        retorna primero Sum(1, (j, 1, n-i)) y luego la externa.
        
        Returns:
            Lista de sumatorias ordenadas de más profunda (interna) a más superficial (externa)
        """
        sums = []
        
        # Primero buscar sumatorias en los argumentos (recursión profunda)
        if hasattr(expr, 'args'):
            for arg in expr.args:
                sums.extend(self._find_sums(arg))
        
        # Luego agregar esta sumatoria (si lo es)
        # Esto garantiza que las internas se agreguen antes que las externas
        if isinstance(expr, Sum):
            sums.append(expr)
        
        return sums
    
    def _parse_expression(self, expr_str: str) -> sp.Expr:
        """
        Parsea un string a expresión SymPy.
        
        Soporta:
        - Sum(expr, (var, start, end)): Sumatoria
        - Expresiones algebraicas: n**2, 3*n + 1, etc.
        - min/max: se convierten a Min/Max de SymPy
        
        Args:
            expr_str: String con la expresión
            
        Returns:
            Expresión SymPy
        """
        # Reemplazar operadores
        expr_str = expr_str.replace("^", "**")
        
        # Convertir min/max a Min/Max de SymPy
        expr_str = re.sub(r'\bmin\b', 'Min', expr_str)
        expr_str = re.sub(r'\bmax\b', 'Max', expr_str)
        
        # IMPORTANTE: Pre-procesar sumatorias anidadas para evitar ambigüedad
        # Reemplazar variables de índice para hacerlas únicas
        # Ejemplo: Sum(Sum(..., (k, 1, n-i)), (k, 1, n-1))
        # La 'k' interna y externa son diferentes, pero SymPy las confunde
        expr_str = self._fix_nested_sums(expr_str)
        
        # Crear namespace con símbolos y funciones
        namespace = {
            'n': self.n,
            'i': self.i,
            'j': self.j,
            'k': self.k,
            'm': self.m,
            'Sum': Sum,
            'Min': sp.Min,
            'Max': sp.Max,
        }
        
        # Parsear usando eval con namespace controlado
        # Esto es más robusto para sumatorias anidadas que sympify
        try:
            expr = eval(expr_str, {"__builtins__": {}}, namespace)
            # Convertir a SymPy si es un tipo Python nativo (int, float)
            if isinstance(expr, (int, float)):
                expr = sp.sympify(expr)
            return expr
        except Exception as e:
            # Si eval falla, intentar con sympify como respaldo
            try:
                expr = sympify(expr_str, locals=namespace)
                return expr
            except:
                raise ValueError(f"No se pudo parsear: {expr_str}. Error: {e}")
    
    def _extract_big_o(self, expr: sp.Expr) -> str:
        """
        Extrae el término dominante (Big-O) de una expresión.
        
        Args:
            expr: Expresión SymPy simplificada
            
        Returns:
            String con notación O(...) del término dominante
        """
        if expr == 0:
            return "O(1)"
        
        try:
            # Si es un símbolo desconocido, retornarlo como es
            if str(expr).startswith("unknown"):
                return f"O({expr})"
            
            # Expandir la expresión
            expr_expanded = sp.expand(expr)
            
            # Obtener términos
            if expr_expanded.is_Add:
                terms = expr_expanded.as_ordered_terms()
            else:
                terms = [expr_expanded]
            
            # Encontrar término dominante (mayor grado en n)
            max_degree = -1
            dominant_term = sp.Integer(1)
            
            for term in terms:
                # Calcular grado respecto a n
                degree = self._get_degree(term, self.n)
                
                if degree > max_degree:
                    max_degree = degree
                    # Extraer solo la parte que depende de n
                    dominant_term = self._extract_n_dependency(term)
            
            # Formatear como O(...)
            if max_degree == 0:
                return "O(1)"
            elif max_degree == 1:
                return "O(n)"
            elif max_degree == 2:
                return "O(n**2)"
            else:
                return f"O({dominant_term})"
                
        except Exception as e:
            # Si falla, retornar O(expr)
            return f"O({expr})"
    
    def _get_degree(self, expr: sp.Expr, var: sp.Symbol) -> int:
        """
        Obtiene el grado de un término respecto a una variable.
        
        Args:
            expr: Expresión SymPy
            var: Variable respecto a la cual calcular el grado
            
        Returns:
            Grado del término
        """
        try:
            # Si es un polinomio, obtener grado directamente
            if expr.is_polynomial(var):
                poly = Poly(expr, var)
                return poly.degree()
            
            # Si contiene log, considerar grado fraccionario
            if expr.has(sp.log):
                # log(n) tiene "grado" 0.5 (entre constante y lineal)
                return 0
            
            # Si no, intentar extraer exponente
            if expr.has(var):
                # Buscar el exponente más alto
                max_exp = 0
                for arg in sp.preorder_traversal(expr):
                    if arg.is_Pow and arg.base == var:
                        exp = arg.exp
                        if exp.is_number:
                            max_exp = max(max_exp, int(exp))
                return max_exp
            
            return 0
            
        except:
            return 0
    
    def _extract_n_dependency(self, expr: sp.Expr) -> sp.Expr:
        """
        Extrae solo la dependencia en n de un término (sin coeficientes).
        
        Args:
            expr: Expresión SymPy
            
        Returns:
            Expresión solo con dependencia en n
        """
        if not expr.has(self.n):
            return sp.Integer(1)
        
        try:
            # Si es un producto, extraer solo las partes con n
            if expr.is_Mul:
                n_parts = []
                for arg in expr.args:
                    if arg.has(self.n):
                        n_parts.append(arg)
                
                if n_parts:
                    return sp.Mul(*n_parts)
            
            # Si es una potencia con base n
            if expr.is_Pow and expr.base == self.n:
                return expr
            
            # Si ya es solo n o función de n
            return expr
            
        except:
            return expr
    
    def _calculate_bounds(
        self,
        best_expr: sp.Expr,
        avg_expr: sp.Expr,
        worst_expr: sp.Expr
    ) -> AsymptoticBounds:
        """
        Calcula las cotas asintóticas Ω, Θ, O.
        
        Ω (omega): Cota inferior = best case
        Θ (theta): Cota ajustada = avg case (o best si avg == worst)
        O (big-o): Cota superior = worst case
        
        Args:
            best_expr: Expresión del mejor caso
            avg_expr: Expresión del caso promedio
            worst_expr: Expresión del peor caso
            
        Returns:
            AsymptoticBounds con Ω, Θ, O
        """
        # Extraer Big-O de cada caso
        best_big_o = self._extract_big_o(best_expr)
        avg_big_o = self._extract_big_o(avg_expr)
        worst_big_o = self._extract_big_o(worst_expr)
        
        # Omega: cota inferior (mejor caso)
        omega = best_big_o.replace("O(", "Ω(")
        
        # Big-O: cota superior (peor caso)
        big_o = worst_big_o
        
        # Theta: cota ajustada
        # Si best y worst tienen la misma complejidad, usar esa
        # Si no, usar caso promedio
        if best_big_o == worst_big_o:
            theta = best_big_o.replace("O(", "Θ(")
        else:
            theta = avg_big_o.replace("O(", "Θ(")
        
        return AsymptoticBounds(
            omega=omega,
            theta=theta,
            big_o=big_o
        )


class SeriesSolverAgent:
    """
    Wrapper del SeriesSolver con interfaz compatible con LangGraph.
    """
    
    def __init__(self):
        """Inicializa el agente con un solver interno."""
        self.solver = SeriesSolver()
    
    def solve(self, cost_expr: CostExpr, show_steps: bool = True, per_line_costs: list = None) -> SolveOut:
        """
        Resuelve una expresión de costo.
        
        Args:
            cost_expr: Expresión de costo a resolver
            show_steps: Si True, genera pasos de resolución
            per_line_costs: Lista opcional de LineCost para solución línea por línea
            
        Returns:
            SolveOut con soluciones y cotas
        """
        return self.solver.solve(cost_expr, show_steps=show_steps, per_line_costs=per_line_costs)
    
    def __call__(self, state: Dict) -> Dict:
        """
        Interfaz LangGraph: recibe estado con 'costs', retorna con 'solution'.
        
        Args:
            state: Dict con clave 'costs' (CostExpr)
            
        Returns:
            Dict con 'solution' (SolveOut), 'success', 'error'
        """
        try:
            costs = state.get("costs")
            
            if costs is None:
                return {
                    "success": False,
                    "error": "No se encontró 'costs' en el estado",
                    "solution": None
                }
            
            # Si costs es CostsOut, usar el total
            if hasattr(costs, "total"):
                costs = costs.total
            
            solution = self.solve(costs)
            
            return {
                "solution": solution,
                "success": True,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "solution": None
            }


# Singleton para el solver
_solver_instance: Optional[SeriesSolverAgent] = None


def get_series_solver() -> SeriesSolverAgent:
    """
    Obtiene la instancia singleton del series solver.
    
    Returns:
        SeriesSolverAgent instancia única
    """
    global _solver_instance
    if _solver_instance is None:
        _solver_instance = SeriesSolverAgent()
    return _solver_instance
