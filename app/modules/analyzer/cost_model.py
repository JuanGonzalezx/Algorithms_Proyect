"""
Cost Analyzer Agent - Convierte AST a expresiones de costo (sumatorias)

Este agente recorre el AST y calcula el costo de cada nodo en términos
de sumatorias simbólicas, considerando los tres casos: mejor, promedio y peor.
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import sympy as sp
from sympy import sympify, simplify
from app.models.ast_nodes import (
    Program, Function, Block, Stmt,
    For, While, If, Assign, Return, ExprStmt,
    Expr, Var, Literal, BinOp, Compare
)
from app.shared.models import CostExpr, NodeCost, LineCost, CostsOut


class CostContext:
    """Contexto para el análisis de costos."""
    
    def __init__(self):
        self.node_counter = 0
        self.loop_depth = 0
        self.var_mapping: Dict[str, str] = {}  # Mapeo: variable original → variable de sumatoria
        self.execution_multipliers: List[str] = []  # Stack de multiplicadores de ejecución
    
    def next_id(self, prefix: str = "N") -> str:
        """Genera un ID único para un nodo."""
        self.node_counter += 1
        return f"{prefix}{self.node_counter}"
    
    def next_loop_var(self) -> str:
        """
        Genera la siguiente variable de loop basada en la profundidad.
        
        Returns:
            Variable de loop: i, j, k, l, m, ...
        """
        vars = ['i', 'j', 'k', 'l', 'm', 'p', 'q', 'r']
        if self.loop_depth < len(vars):
            return vars[self.loop_depth]
        return f"v{self.loop_depth}"
    
    def get_execution_count(self) -> str:
        """
        Retorna el número de veces que se ejecuta el código actual.
        Es el producto de todas las iteraciones de los loops padre.
        """
        if not self.execution_multipliers:
            return "1"
        if len(self.execution_multipliers) == 1:
            return self.execution_multipliers[0]
        # Producto de todos los multiplicadores
        result = " * ".join(f"({m})" for m in self.execution_multipliers)
        return result
    
    def replace_vars(self, expr: str) -> str:
        """
        Reemplaza variables originales por variables de sumatoria en una expresión.
        
        Args:
            expr: Expresión que puede contener variables originales del código
            
        Returns:
            Expresión con variables reemplazadas
        """
        result = expr
        for orig_var, sum_var in self.var_mapping.items():
            result = result.replace(orig_var, sum_var)
        return result


class CostAnalyzer:
    """
    Analizador de costos que recorre el AST y genera expresiones de costo.
    
    REGLAS DE COSTEO:
    - Literal/Var: 0
    - BinOp/Compare: 1 + coste(izq) + coste(der)
    - Assign: 1 + coste(RHS)
    - ExprStmt: coste(expr)
    - If: coste(Cond) + {best: min, avg: p*then + (1-p)*else, worst: max}
    - For: Sum(cuerpo) + [opcional: control con tests = (b-a+2)]
    - While: best=guard, avg/worst=M*guard + Sum(body) + guard
    
    BANDERAS DE CONFIGURACIÓN:
    """
    
    # Configuración de análisis
    COUNT_LOOP_CONTROL = False  # Si True, añade coste de control de loops (init, tests, increments)
    INCREMENT_STYLE = "unit"    # "unit" (i++) o "expanded" (i <- i + 1)
    DEFAULT_P_TRUE = 0.5        # Probabilidad por defecto para ramas condicionales
    
    def __init__(self):
        self.context = CostContext()
        self.costs: List[NodeCost] = []
    
    @staticmethod
    def _simplify_expr(expr_str: str) -> str:
        """
        Simplifica una expresión usando SymPy.
        
        Args:
            expr_str: Expresión en formato string
            
        Returns:
            Expresión simplificada como string
        """
        if not expr_str or expr_str == "0" or expr_str == "1":
            return expr_str
        
        try:
            # Parsear la expresión (sympify reconoce automáticamente variables)
            expr = sympify(expr_str, evaluate=True)
            # Simplificar
            simplified = simplify(expr)
            return str(simplified)
        except Exception as e:
            # Si falla la simplificación, retornar original
            return expr_str
    
    def analyze(self, program: Program, source_code: str = "") -> CostsOut:
        """
        Analiza el programa completo y retorna los costos.
        
        Args:
            program: AST del programa
            source_code: Código fuente original (opcional, para generar costos por línea)
            
        Returns:
            CostsOut con costos por nodo, por línea y total
        """
        self.context = CostContext()
        self.costs = []
        
        # Analizar el programa
        total_cost = self._analyze_program(program)
        
        # Generar costos por línea si hay código fuente
        per_line = self._generate_line_costs(source_code) if source_code else []
        
        return CostsOut(
            per_node=self.costs,
            per_line=per_line,
            total=total_cost
        )
    
    def _analyze_program(self, program: Program) -> CostExpr:
        """Analiza el programa completo."""
        node_id = self.context.next_id("Prog")
        
        # Analizar cada función
        function_costs = []
        for func in program.functions:
            cost = self._analyze_function(func)
            function_costs.append(cost)
        
        # El costo total es la suma de todas las funciones
        if not function_costs:
            total = CostExpr(best="0", avg="0", worst="0")
        elif len(function_costs) == 1:
            total = function_costs[0]
        else:
            # Sumar todas las funciones
            total = self._sum_costs(function_costs)
        
        # Registrar costo del programa
        self.costs.append(NodeCost(
            node_id=node_id,
            node_type="Program",
            cost=total
        ))
        
        return total
    
    def _analyze_function(self, func: Function) -> CostExpr:
        """Analiza una función."""
        node_id = self.context.next_id("Func")
        
        # Analizar el body de la función
        cost = self._analyze_block(func.body)
        
        # Registrar costo de la función
        self.costs.append(NodeCost(
            node_id=node_id,
            node_type="Function",
            cost=cost
        ))
        
        return cost
    
    def _analyze_block(self, block: Block) -> CostExpr:
        """Analiza un bloque de statements."""
        if not block.statements:
            return CostExpr(best="0", avg="0", worst="0")
        
        # Analizar cada statement
        statement_costs = []
        for stmt in block.statements:
            cost = self._analyze_statement(stmt)
            statement_costs.append(cost)
        
        # Sumar todos los costos
        return self._sum_costs(statement_costs)
    
    def _analyze_statement(self, stmt: Stmt) -> CostExpr:
        """Analiza un statement y retorna su costo."""
        if isinstance(stmt, For):
            return self._analyze_for(stmt)
        elif isinstance(stmt, While):
            return self._analyze_while(stmt)
        elif isinstance(stmt, If):
            return self._analyze_if(stmt)
        elif isinstance(stmt, Assign):
            return self._analyze_assign(stmt)
        elif isinstance(stmt, Return):
            return self._analyze_return(stmt)
        elif isinstance(stmt, ExprStmt):
            return self._analyze_expr_stmt(stmt)
        else:
            # Statement desconocido, costo 1
            return CostExpr(best="1", avg="1", worst="1")
    
    def _analyze_for(self, for_stmt: For) -> CostExpr:
        """
        Analiza un bucle for con control opcional.
        
        Regla:
        - Iteraciones N = (b - a) + 1 (límite inclusivo)
        - Coste = Sum(costo_body, (var, a, b))
        - Si COUNT_LOOP_CONTROL=True, añadir:
          * init = 1
          * tests = N + 1 = (b - a + 2)
          * increments = N (si INCREMENT_STYLE="unit") o 2*N (si "expanded")
        """
        node_id = self.context.next_id("For")
        
        # Obtener variable de loop única para este nivel
        iter_var = self.context.next_loop_var()
        
        # Guardar mapeo: variable original → variable de sumatoria
        var = for_stmt.var
        self.context.var_mapping[var] = iter_var
        
        # Incrementar profundidad de loop
        self.context.loop_depth += 1
        
        # Analizar el body del for
        body_cost = self._analyze_block(for_stmt.body)
        
        # Decrementar profundidad al salir
        self.context.loop_depth -= 1
        
        # Remover mapeo
        del self.context.var_mapping[var]
        
        # Extraer información del rango y reemplazar variables
        start_expr = self.context.replace_vars(self._expr_to_str(for_stmt.start))
        end_expr = self.context.replace_vars(self._expr_to_str(for_stmt.end))
        
        # También reemplazar variables en el body cost
        body_cost_best = self.context.replace_vars(body_cost.best)
        body_cost_avg = self.context.replace_vars(body_cost.avg)
        body_cost_worst = self.context.replace_vars(body_cost.worst)
        
        # Crear sumatoria: Sum(costo_body, (var, start, end))
        sum_best = self._create_sum(body_cost_best, iter_var, start_expr, end_expr)
        sum_avg = self._create_sum(body_cost_avg, iter_var, start_expr, end_expr)
        sum_worst = self._create_sum(body_cost_worst, iter_var, start_expr, end_expr)
        
        # Si COUNT_LOOP_CONTROL=True, añadir coste de control
        if self.COUNT_LOOP_CONTROL:
            # N = (b - a) + 1
            # init = 1
            # tests = N + 1 = (b - a + 2)
            # increments = N si unit, 2*N si expanded
            
            init_cost = "1"
            tests_cost = f"(({end_expr}) - ({start_expr}) + 2)"
            
            if self.INCREMENT_STYLE == "unit":
                increments_cost = f"(({end_expr}) - ({start_expr}) + 1)"
            else:  # "expanded"
                increments_cost = f"2*(({end_expr}) - ({start_expr}) + 1)"
            
            control_cost = self._add_terms([init_cost, tests_cost, increments_cost])
            
            sum_best = self._add_terms([sum_best, control_cost])
            sum_avg = self._add_terms([sum_avg, control_cost])
            sum_worst = self._add_terms([sum_worst, control_cost])
        
        cost = CostExpr(best=sum_best, avg=sum_avg, worst=sum_worst)
        
        # Calcular costo propio (solo el overhead del for, sin el body)
        if self.COUNT_LOOP_CONTROL:
            # Costo propio = solo el control del loop (init + tests + increments)
            own_cost = CostExpr(best=control_cost, avg=control_cost, worst=control_cost)
        else:
            # Si no contamos control, el costo propio es 0 (solo cuenta el body)
            own_cost = CostExpr(best="0", avg="0", worst="0")
        
        # Extraer información de línea
        line_start, line_end, code_snippet = self._extract_line_info(for_stmt)
        
        # Registrar costo del for
        from app.shared.models import LoopInfo
        self.costs.append(NodeCost(
            node_id=node_id,
            node_type="For",
            line_start=line_start,
            line_end=line_end,
            code_snippet=code_snippet,
            cost=cost,
            own_cost=own_cost,
            loop_info=LoopInfo(var=iter_var, start=start_expr, end=end_expr)
        ))
        
        return cost
    
    def _analyze_while(self, while_stmt: While) -> CostExpr:
        """
        Analiza un bucle while con coste del guard incluido.
        
        Regla:
        - Best: condición falsa al inicio → 1 evaluación del guard
        - Avg: M = n/2 iteraciones → M*guard + Sum(body, (t,1,M)) + guard
        - Worst: M = n iteraciones → n*guard + Sum(body, (t,1,n)) + guard
        
        El guard se evalúa M veces durante las iteraciones + 1 vez final (que falla).
        """
        node_id = self.context.next_id("While")
        
        # Calcular coste del guard (condición)
        guard_cost = self._cost_of_expr(while_stmt.cond)
        
        # Incrementar profundidad de loop
        self.context.loop_depth += 1
        
        # Obtener variable de loop única
        iter_var = self.context.next_loop_var()
        
        # Analizar el body del while
        body_cost = self._analyze_block(while_stmt.body)
        
        # Decrementar profundidad al salir
        self.context.loop_depth -= 1
        
        # Mejor caso: condición falsa al inicio → solo 1 evaluación del guard
        best = guard_cost if guard_cost != "0" else "1"
        
        # Caso promedio: M = n/2 iteraciones
        # Coste = M*guard + Sum(body, (t,1,M)) + guard
        M_avg = "n/2"
        guard_evals_avg = self._multiply_terms(M_avg, guard_cost)
        body_sum_avg = self._create_sum(body_cost.avg, iter_var, "1", M_avg)
        avg = self._add_terms([guard_evals_avg, body_sum_avg, guard_cost])
        
        # Peor caso: M = n iteraciones
        # Coste = n*guard + Sum(body, (t,1,n)) + guard
        M_worst = "n"
        guard_evals_worst = self._multiply_terms(M_worst, guard_cost)
        body_sum_worst = self._create_sum(body_cost.worst, iter_var, "1", M_worst)
        worst = self._add_terms([guard_evals_worst, body_sum_worst, guard_cost])
        
        cost = CostExpr(best=best, avg=avg, worst=worst)
        
        # Costo propio del while = solo las evaluaciones del guard
        # Best: 1 evaluación, Avg: (M_avg+1) evaluaciones, Worst: (M_worst+1) evaluaciones
        own_best = guard_cost
        own_avg = self._add_terms([guard_evals_avg, guard_cost])
        own_worst = self._add_terms([guard_evals_worst, guard_cost])
        own_cost = CostExpr(best=own_best, avg=own_avg, worst=own_worst)
        
        # Extraer información de línea
        line_start, line_end, code_snippet = self._extract_line_info(while_stmt)
        
        # Registrar costo del while
        self.costs.append(NodeCost(
            node_id=node_id,
            node_type="While",
            line_start=line_start,
            line_end=line_end,
            code_snippet=code_snippet,
            cost=cost,
            own_cost=own_cost
        ))
        
        return cost
    
    def _analyze_if(self, if_stmt: If) -> CostExpr:
        """
        Analiza un condicional if con coste del guard incluido.
        
        Regla: coste = coste(Cond) + {best: min, avg: p*then + (1-p)*else, worst: max}
        
        - Best: coste(Cond) + min(then, else)
        - Avg: coste(Cond) + p*then + (1-p)*else  (p = DEFAULT_P_TRUE)
        - Worst: coste(Cond) + max(then, else)
        """
        node_id = self.context.next_id("If")
        
        # Calcular coste del guard (condición)
        guard_cost = self._cost_of_expr(if_stmt.cond)
        
        # Analizar then_block
        then_cost = self._analyze_block(if_stmt.then_block)
        
        # Analizar else_block si existe
        if if_stmt.else_block:
            else_cost = self._analyze_block(if_stmt.else_block)
        else:
            else_cost = CostExpr(best="0", avg="0", worst="0")
        
        # Calcular costos según casos (SIEMPRE incluyendo guard)
        
        # Mejor caso: guard + min(then, else)
        best_branch = self._min_cost(then_cost.best, else_cost.best)
        best = self._add_terms([guard_cost, best_branch])
        
        # Caso promedio: guard + p*then + (1-p)*else
        p = str(self.DEFAULT_P_TRUE)
        one_minus_p = str(1 - self.DEFAULT_P_TRUE)
        avg_then = self._multiply_terms(p, then_cost.avg)
        avg_else = self._multiply_terms(one_minus_p, else_cost.avg)
        avg = self._add_terms([guard_cost, avg_then, avg_else])
        
        # Peor caso: guard + max(then, else)
        worst_branch = self._max_cost(then_cost.worst, else_cost.worst)
        worst = self._add_terms([guard_cost, worst_branch])
        
        cost = CostExpr(best=best, avg=avg, worst=worst)
        
        # Costo propio del if = solo el guard (la evaluación de la condición)
        own_cost = CostExpr(best=guard_cost, avg=guard_cost, worst=guard_cost)
        
        # Extraer información de línea
        line_start, line_end, code_snippet = self._extract_line_info(if_stmt)
        
        # Registrar costo del if
        self.costs.append(NodeCost(
            node_id=node_id,
            node_type="If",
            line_start=line_start,
            line_end=line_end,
            code_snippet=code_snippet,
            cost=cost,
            own_cost=own_cost
        ))
        
        return cost
    
    def _analyze_assign(self, assign: Assign) -> CostExpr:
        """
        Analiza una asignación: 1 (operador de asignar) + coste de evaluar RHS.
        
        Regla: x <- expr  =>  coste = 1 + coste(expr)
        """
        node_id = self.context.next_id("Assign")
        
        # Calcular coste del lado derecho
        rhs_cost = self._cost_of_expr(assign.value)
        
        # Coste total: 1 (asignación) + coste(RHS)
        total_cost = self._add_terms(["1", rhs_cost])
        
        cost = CostExpr(best=total_cost, avg=total_cost, worst=total_cost)
        
        # Para Assign, el costo propio es el mismo que el total (no tiene hijos)
        own_cost = cost
        
        # Extraer información de línea
        line_start, line_end, code_snippet = self._extract_line_info(assign)
        
        self.costs.append(NodeCost(
            node_id=node_id,
            node_type="Assign",
            line_start=line_start,
            line_end=line_end,
            code_snippet=code_snippet,
            cost=cost,
            own_cost=own_cost
        ))
        
        return cost
    
    def _analyze_return(self, return_stmt: Return) -> CostExpr:
        """Analiza un return: costo constante 1."""
        node_id = self.context.next_id("Return")
        
        cost = CostExpr(best="1", avg="1", worst="1")
        
        self.costs.append(NodeCost(
            node_id=node_id,
            node_type="Return",
            cost=cost
        ))
        
        return cost
    
    def _analyze_expr_stmt(self, expr_stmt: ExprStmt) -> CostExpr:
        """
        Analiza una expresión statement: coste de evaluar la expresión.
        
        Regla: coste = coste(expr)
        """
        node_id = self.context.next_id("ExprStmt")
        
        # Calcular coste de la expresión
        expr_cost = self._cost_of_expr(expr_stmt.expr)
        
        # Si el coste es 0 (ej: solo una variable), considerar al menos 1
        if expr_cost == "0":
            expr_cost = "1"
        
        cost = CostExpr(best=expr_cost, avg=expr_cost, worst=expr_cost)
        
        self.costs.append(NodeCost(
            node_id=node_id,
            node_type="ExprStmt",
            cost=cost
        ))
        
        return cost
    
    # ======== HELPERS PARA EXPRESIONES ========
    
    def _extract_line_info(self, stmt: Stmt) -> tuple:
        """
        Extrae información de línea del statement para el frontend.
        
        Returns:
            tuple: (line_start, line_end, code_snippet)
        """
        line_start = getattr(stmt, 'line_start', None)
        line_end = getattr(stmt, 'line_end', None)
        code_snippet = None
        
        # Generar un snippet básico del código
        if hasattr(stmt, '__class__'):
            stmt_type = stmt.__class__.__name__
            if stmt_type == 'For' and hasattr(stmt, 'var'):
                code_snippet = f"for {stmt.var} ← ... to ..."
            elif stmt_type == 'While':
                code_snippet = "while ..."
            elif stmt_type == 'If':
                code_snippet = "if ..."
            elif stmt_type == 'Assign' and hasattr(stmt, 'target'):
                target_name = stmt.target.name if hasattr(stmt.target, 'name') else '...'
                code_snippet = f"{target_name} ← ..."
            elif stmt_type == 'Return':
                code_snippet = "return ..."
        
        return line_start, line_end, code_snippet
    
    def _cost_of_expr(self, expr: Expr) -> str:
        """
        Calcula el coste de evaluar una expresión.
        
        Reglas:
        - Literal, Var: 0
        - BinOp: 1 + coste(izq) + coste(der)
        - Compare: 1 + coste(izq) + coste(der)
        
        Returns:
            String con el coste (puede ser "0", "1", "2", etc.)
        """
        if isinstance(expr, (Literal, Var)):
            return "0"
        elif isinstance(expr, BinOp):
            left_cost = self._cost_of_expr(expr.left)
            right_cost = self._cost_of_expr(expr.right)
            # 1 (operador) + coste(izq) + coste(der)
            return self._add_terms(["1", left_cost, right_cost])
        elif isinstance(expr, Compare):
            left_cost = self._cost_of_expr(expr.left)
            right_cost = self._cost_of_expr(expr.right)
            # 1 (comparador) + coste(izq) + coste(der)
            return self._add_terms(["1", left_cost, right_cost])
        else:
            # Expresión desconocida, asumir coste 0
            return "0"
    
    def _add_terms(self, terms: List[str]) -> str:
        """
        Suma términos eliminando ceros y evitando redundancias.
        
        Args:
            terms: Lista de strings representando términos
            
        Returns:
            String con la suma (e.g., "1 + n", "2", "0")
        """
        # Filtrar ceros
        non_zero = [t for t in terms if t != "0"]
        
        if not non_zero:
            return "0"
        
        if len(non_zero) == 1:
            return non_zero[0]
        
        # Unir con " + "
        return " + ".join(non_zero)
    
    def _multiply_terms(self, factor: str, expr: str) -> str:
        """
        Multiplica un factor por una expresión, evitando * 0 y * 1.
        
        Args:
            factor: Factor multiplicador (e.g., "n", "0.5")
            expr: Expresión a multiplicar
            
        Returns:
            String con el producto
        """
        if factor == "0" or expr == "0":
            return "0"
        if factor == "1":
            return expr
        if expr == "1":
            return factor
        
        # Si expr tiene suma, necesita paréntesis
        if "+" in expr or "-" in expr:
            return f"{factor}*({expr})"
        
        return f"{factor}*{expr}"
    
    # ======== UTILIDADES ========
    
    def _sum_costs(self, costs: List[CostExpr]) -> CostExpr:
        """Suma una lista de expresiones de costo."""
        if not costs:
            return CostExpr(best="0", avg="0", worst="0")
        
        if len(costs) == 1:
            return costs[0]
        
        # Construir suma para cada caso
        best_terms = [c.best for c in costs if c.best != "0"]
        avg_terms = [c.avg for c in costs if c.avg != "0"]
        worst_terms = [c.worst for c in costs if c.worst != "0"]
        
        best = " + ".join(best_terms) if best_terms else "0"
        avg = " + ".join(avg_terms) if avg_terms else "0"
        worst = " + ".join(worst_terms) if worst_terms else "0"
        
        return CostExpr(best=best, avg=avg, worst=worst)
    
    def _create_sum(self, inner_expr: str, var: str, start: str, end: str) -> str:
        """Crea una expresión Sum."""
        if inner_expr == "0":
            return "0"
        return f"Sum({inner_expr}, ({var}, {start}, {end}))"
    
    def _expr_to_str(self, expr: Expr) -> str:
        """Convierte una expresión AST a string."""
        if isinstance(expr, Literal):
            return str(expr.value)
        elif isinstance(expr, Var):
            return expr.name
        elif isinstance(expr, BinOp):
            left = self._expr_to_str(expr.left)
            right = self._expr_to_str(expr.right)
            return f"({left} {expr.op} {right})"
        else:
            return "n"  # Valor por defecto
    
    def _min_cost(self, cost1: str, cost2: str) -> str:
        """Calcula el mínimo entre dos costos."""
        if cost1 == "0":
            return "0"
        if cost2 == "0":
            return "0"
        if cost1 == cost2:
            return cost1
        return f"min({cost1}, {cost2})"
    
    def _max_cost(self, cost1: str, cost2: str) -> str:
        """Calcula el máximo entre dos costos."""
        if cost1 == cost2:
            return cost1
        return f"max({cost1}, {cost2})"
    
    def _avg_cost(self, cost1: str, cost2: str) -> str:
        """Calcula el promedio entre dos costos."""
        if cost1 == "0" and cost2 == "0":
            return "0"
        if cost1 == cost2:
            return cost1
        return f"({cost1} + {cost2})/2"
    
    def _generate_line_costs(self, source_code: str) -> List[LineCost]:
        """
        Genera costos por línea basándose en cuántas veces se ejecuta cada línea.
        
        El costo de una línea = costo_propio * número_de_ejecuciones
        
        Args:
            source_code: Código fuente del programa
            
        Returns:
            Lista de LineCost con el costo total de cada línea (own_cost * execution_count)
        """
        if not source_code:
            return []
        
        lines = source_code.split('\n')
        
        # Encontrar todos los For nodes con loop_info
        for_nodes = [node for node in self.costs 
                    if node.node_type == "For" and node.loop_info and node.line_start and node.line_end]
        
        # Ordenar por rango (los más externos primero)
        for_nodes.sort(key=lambda n: (n.line_start, -n.line_end))
        
        # Encontrar todos los If nodes
        if_nodes = [node for node in self.costs 
                   if node.node_type == "If" and node.line_start and node.line_end]
        
        # Ordenar por rango (los más externos primero)
        if_nodes.sort(key=lambda n: (n.line_start, -n.line_end))
        
        # Crear un mapa: line_number -> [list of LoopInfo que la contienen]
        line_to_loops = {}
        for line_num in range(1, len(lines) + 1):
            containing_loops = []
            for for_node in for_nodes:
                # Verificar si esta línea está DENTRO del for (no en la línea del for mismo)
                if for_node.line_start < line_num <= for_node.line_end:
                    containing_loops.append((for_node.loop_info.var, 
                                            for_node.loop_info.start, 
                                            for_node.loop_info.end))
            if containing_loops:
                line_to_loops[line_num] = containing_loops
        
        # Crear un mapa: line_number -> número de ifs que la contienen (para probabilidades)
        # En realidad necesitamos saber si está en el then o else de cada if
        line_to_if_depth = {}
        for line_num in range(1, len(lines) + 1):
            if_depth = 0
            for if_node in if_nodes:
                # Verificar si esta línea está DENTRO del if (no en la línea del if mismo)
                if if_node.line_start < line_num <= if_node.line_end:
                    if_depth += 1
            if if_depth > 0:
                line_to_if_depth[line_num] = if_depth
        
        # Ahora calcular el costo de cada línea
        line_costs_map = {}
        
        for node in self.costs:
            # Procesar TODOS los nodos que tienen línea asociada (excepto Function y Program)
            if not node.line_start or node.node_type in ['Function', 'Program']:
                continue
            
            line_num = node.line_start
            
            # Para nodos For/While, calculamos cuántas veces se EJECUTA/EVALÚA el for mismo
            if node.node_type == 'For':
                # Para un for loop, la línea se ejecuta: (end - start + 2) veces
                # Ejemplo: for i = 1 to n → se ejecuta n+1 veces (n veces entra + 1 vez sale)
                # Si el for está dentro de otro for, multiplicamos por las iteraciones del padre
                
                if node.loop_info:
                    # Número de evaluaciones del for = (end - start) + 2
                    # Usamos 1 como costo base (1 evaluación = 1 operación)
                    start = node.loop_info.start
                    end = node.loop_info.end
                    # Simplificar la expresión: (n-1) - 1 + 2 = n
                    num_evaluations_raw = f"({end}) - ({start}) + 2"
                    num_evaluations = self._simplify_expr(num_evaluations_raw)
                    
                    # Si este for está dentro de otros fors, multiplicar
                    containing_loops = line_to_loops.get(line_num, [])
                    if containing_loops:
                        execution_cost_best = self._wrap_in_sums(num_evaluations, containing_loops)
                        execution_cost_avg = self._wrap_in_sums(num_evaluations, containing_loops)
                        execution_cost_worst = self._wrap_in_sums(num_evaluations, containing_loops)
                    else:
                        execution_cost_best = num_evaluations
                        execution_cost_avg = num_evaluations
                        execution_cost_worst = num_evaluations
                else:
                    # Fallback si no hay loop_info
                    execution_cost_best = "1"
                    execution_cost_avg = "1"
                    execution_cost_worst = "1"
            elif node.node_type == 'While':
                # Para while, es más complejo, por ahora usamos el own_cost
                if node.own_cost:
                    execution_cost_best = node.own_cost.best
                    execution_cost_avg = node.own_cost.avg
                    execution_cost_worst = node.own_cost.worst
                else:
                    execution_cost_best = "0"
                    execution_cost_avg = "0"
                    execution_cost_worst = "0"
            else:
                # Para otros nodos (Assign, If, etc.), aplicar multiplicadores de loops
                if not node.own_cost:
                    continue  # Skip nodos sin own_cost
                
                containing_loops = line_to_loops.get(line_num, [])
                if_depth = line_to_if_depth.get(line_num, 0)
                
                # Comenzar con el costo propio del nodo
                base_cost_best = node.own_cost.best
                base_cost_avg = node.own_cost.avg
                base_cost_worst = node.own_cost.worst
                
                # Si está dentro de condicionales, aplicar probabilidades
                if if_depth > 0:
                    # Best case: el if casi nunca entra (probabilidad muy baja)
                    # Para simplificar, usamos 0 (el if nunca entra en el mejor caso)
                    base_cost_best = "0"
                    
                    # Average case: el if entra ~50% de las veces
                    # Multiplicamos por 0.5^if_depth
                    probability = 0.5 ** if_depth
                    if base_cost_avg != "0":
                        base_cost_avg = f"({probability} * ({base_cost_avg}))"
                    
                    # Worst case: el if siempre entra (probabilidad = 1.0)
                    # No cambia el costo
                
                # Aplicar multiplicadores de loops
                if containing_loops:
                    execution_cost_best = self._wrap_in_sums(base_cost_best, containing_loops)
                    execution_cost_avg = self._wrap_in_sums(base_cost_avg, containing_loops)
                    execution_cost_worst = self._wrap_in_sums(base_cost_worst, containing_loops)
                else:
                    # No está en ningún loop
                    execution_cost_best = base_cost_best
                    execution_cost_avg = base_cost_avg
                    execution_cost_worst = base_cost_worst
            
            if line_num not in line_costs_map:
                line_costs_map[line_num] = {
                    'operations': [],
                    'costs_best': [],
                    'costs_avg': [],
                    'costs_worst': []
                }
            
            line_costs_map[line_num]['operations'].append(node.node_type)
            line_costs_map[line_num]['costs_best'].append(execution_cost_best)
            line_costs_map[line_num]['costs_avg'].append(execution_cost_avg)
            line_costs_map[line_num]['costs_worst'].append(execution_cost_worst)
        
        # Crear LineCost para cada línea
        result = []
        for line_num in sorted(line_costs_map.keys()):
            if 1 <= line_num <= len(lines):
                data = line_costs_map[line_num]
                
                # Sumar todos los costos de operaciones en esta línea
                best_sum = self._add_terms(data['costs_best'])
                avg_sum = self._add_terms(data['costs_avg'])
                worst_sum = self._add_terms(data['costs_worst'])
                
                result.append(LineCost(
                    line_number=line_num,
                    code=lines[line_num - 1],
                    operations=data['operations'],
                    cost=CostExpr(best=best_sum, avg=avg_sum, worst=worst_sum)
                ))
        
        return result
    
    def _wrap_in_sums(self, base_cost: str, loops: List[Tuple[str, str, str]]) -> str:
        """
        Envuelve un costo base en sumatorias según los loops que lo contienen.
        
        Args:
            base_cost: Costo base (ej: "1")
            loops: Lista de (var, start, end) de los loops, desde el más externo al más interno
            
        Returns:
            Expresión con sumatorias anidadas
        """
        result = base_cost
        # Envolver de adentro hacia afuera (loops internos primero)
        for var, start, end in reversed(loops):
            result = self._create_sum(result, var, start, end)
        return result


class CostAnalyzerAgent:
    """
    Agente de análisis de costos.
    
    Recibe un AST y genera expresiones de costo simbólicas
    para cada nodo y el programa completo.
    """
    
    def __init__(self):
        self.analyzer = CostAnalyzer()
    
    def analyze(self, program: Program, source_code: str = "") -> CostsOut:
        """
        Analiza el programa y retorna los costos.
        
        Args:
            program: AST del programa (objeto Program)
            source_code: Código fuente original (opcional, para generar costos por línea)
            
        Returns:
            CostsOut con costos por nodo, por línea y total
        """
        return self.analyzer.analyze(program, source_code)
    
    def __call__(self, input_data: dict) -> dict:
        """
        Interfaz compatible con LangGraph.
        
        Args:
            input_data: {"ast": Program, "source_code": str (opcional)}
            
        Returns:
            {"costs": CostsOut, "success": bool, "error": Optional[str]}
        """
        try:
            ast = input_data.get("ast")
            source_code = input_data.get("source_code", "")
            
            if not isinstance(ast, Program):
                raise ValueError("Input 'ast' debe ser un objeto Program")
            
            costs = self.analyze(ast, source_code)
            
            return {
                "costs": costs,
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "costs": None,
                "success": False,
                "error": str(e)
            }


# Singleton global
_cost_analyzer = None

def get_cost_analyzer() -> CostAnalyzerAgent:
    """Retorna instancia singleton del cost analyzer."""
    global _cost_analyzer
    if _cost_analyzer is None:
        _cost_analyzer = CostAnalyzerAgent()
    return _cost_analyzer
