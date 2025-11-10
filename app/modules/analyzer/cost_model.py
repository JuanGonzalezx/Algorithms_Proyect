# app/modules/analyzer/agent.py
from typing import Dict, List, Tuple
import sympy as sp
from sympy import sympify, simplify
from app.models.ast_nodes import (
    Program, Function, Block, Stmt,
    For, While, If, Assign, Return, ExprStmt,
    Expr, Var, Literal, BinOp, Compare
)
from app.shared.models import CostExpr, NodeCost, LineCost, CostsOut


class CostContext:
    def __init__(self):
        self.node_counter = 0
        self.loop_depth = 0
        self.var_mapping: Dict[str, str] = {}      # var original -> var de sumatoria
        self.execution_multipliers: List[str] = [] # (no usado fuera de get_execution_count)

    def next_id(self, prefix: str = "N") -> str:
        self.node_counter += 1
        return f"{prefix}{self.node_counter}"

    def next_loop_var(self) -> str:
        vars_ = ['i', 'j', 'k', 'l', 'm', 'p', 'q', 'r']
        return vars_[self.loop_depth] if self.loop_depth < len(vars_) else f"v{self.loop_depth}"

    def get_execution_count(self) -> str:
        if not self.execution_multipliers:
            return "1"
        return " * ".join(f"({m})" for m in self.execution_multipliers)

    def replace_vars(self, expr: str) -> str:
        out = expr
        for orig, repl in self.var_mapping.items():
            out = out.replace(orig, repl)
        return out


class CostAnalyzer:
    # Config
    COUNT_LOOP_CONTROL = False
    INCREMENT_STYLE = "unit"
    DEFAULT_P_TRUE = 0.5

    def __init__(self):
        self.context = CostContext()
        self.costs: List[NodeCost] = []

    @staticmethod
    def _simplify_expr(expr_str: str) -> str:
        if not expr_str or expr_str in ("0", "1"):
            return expr_str
        try:
            return str(simplify(sympify(expr_str, evaluate=True)))
        except Exception:
            return expr_str

    def analyze(self, program: Program, source_code: str = "") -> CostsOut:
        """
        IMPORTANTE: total ahora se calcula SIEMPRE como suma de costos por línea.
        (El análisis por bloques solo se usa para poblar per_node/per_line)
        """
        self.context = CostContext()
        self.costs = []

        # Poblar costos por nodo (necesario para saber rangos de líneas y loops)
        _ = self._analyze_program(program)

        # Costeo por línea (MVP canónico)
        per_line = self._generate_line_costs(source_code) if source_code else []

        # Total = suma de expresiones de cada línea (best/avg/worst)
        total = self._sum_from_lines(per_line) if per_line else CostExpr(best="0", avg="0", worst="0")

        return CostsOut(per_node=self.costs, per_line=per_line, total=total)

    # ---- Programa / función / bloque ----
    def _analyze_program(self, program: Program) -> CostExpr:
        node_id = self.context.next_id("Prog")
        fn_costs = [self._analyze_function(f) for f in program.functions]
        total = self._sum_costs(fn_costs) if fn_costs else CostExpr(best="0", avg="0", worst="0")
        self.costs.append(NodeCost(node_id=node_id, node_type="Program", cost=total))
        return total

    def _analyze_function(self, func: Function) -> CostExpr:
        node_id = self.context.next_id("Func")
        cost = self._analyze_block(func.body)
        self.costs.append(NodeCost(node_id=node_id, node_type="Function", cost=cost))
        return cost

    def _analyze_block(self, block: Block) -> CostExpr:
        if not block.statements:
            return CostExpr(best="0", avg="0", worst="0")
        return self._sum_costs([self._analyze_statement(s) for s in block.statements])

    def _analyze_statement(self, stmt: Stmt) -> CostExpr:
        if isinstance(stmt, For):    return self._analyze_for(stmt)
        if isinstance(stmt, While):  return self._analyze_while(stmt)
        if isinstance(stmt, If):     return self._analyze_if(stmt)
        if isinstance(stmt, Assign): return self._analyze_assign(stmt)
        if isinstance(stmt, Return): return CostExpr(best="1", avg="1", worst="1")
        if isinstance(stmt, ExprStmt): return self._analyze_expr_stmt(stmt)
        return CostExpr(best="1", avg="1", worst="1")

    # ---- For ----
    def _analyze_for(self, for_stmt: For) -> CostExpr:
        node_id = self.context.next_id("For")
        iter_var = self.context.next_loop_var()
        self.context.var_mapping[for_stmt.var] = iter_var
        self.context.loop_depth += 1
        body_cost = self._analyze_block(for_stmt.body)
        self.context.loop_depth -= 1
        del self.context.var_mapping[for_stmt.var]

        start = self.context.replace_vars(self._expr_to_str(for_stmt.start))
        end   = self.context.replace_vars(self._expr_to_str(for_stmt.end))
        b, a, w = (self.context.replace_vars(body_cost.best),
                   self.context.replace_vars(body_cost.avg),
                   self.context.replace_vars(body_cost.worst))

        sum_best  = self._create_sum(b, iter_var, start, end)
        sum_avg   = self._create_sum(a, iter_var, start, end)
        sum_worst = self._create_sum(w, iter_var, start, end)

        if self.COUNT_LOOP_CONTROL:
            init_cost = "1"
            tests_cost = f"(({end}) - ({start}) + 2)"
            inc = f"(({end}) - ({start}) + 1)"
            if self.INCREMENT_STYLE != "unit":
                inc = f"2*{inc}"
            control = self._add_terms([init_cost, tests_cost, inc])
            sum_best  = self._add_terms([sum_best, control])
            sum_avg   = self._add_terms([sum_avg, control])
            sum_worst = self._add_terms([sum_worst, control])
            own_cost = CostExpr(best=control, avg=control, worst=control)
        else:
            own_cost = CostExpr(best="0", avg="0", worst="0")

        cost = CostExpr(best=sum_best, avg=sum_avg, worst=sum_worst)
        ls, le, snippet = self._extract_line_info(for_stmt)
        from app.shared.models import LoopInfo
        self.costs.append(NodeCost(
            node_id=node_id, node_type="For",
            line_start=ls, line_end=le, code_snippet=snippet,
            cost=cost, own_cost=own_cost,
            loop_info=LoopInfo(var=iter_var, start=start, end=end)
        ))
        return cost

    # ---- While ----
    def _analyze_while(self, while_stmt: While) -> CostExpr:
        node_id = self.context.next_id("While")
        guard = self._cost_of_expr(while_stmt.cond)
        is_nested = self.context.loop_depth > 0
        self.context.loop_depth += 1
        iter_var = self.context.next_loop_var()
        body = self._analyze_block(while_stmt.body)
        self.context.loop_depth -= 1

        best = guard if guard != "0" else "1"

        if is_nested and self.context.loop_depth >= 0:
            # Heurística: usar var del padre
            self.context.loop_depth -= 1
            parent_var = self.context.next_loop_var()
            self.context.loop_depth += 1
            M_avg, M_worst = f"{parent_var}/2", parent_var
        else:
            M_avg, M_worst = "n/2", "n"

        guard_avg   = self._multiply_terms(M_avg, guard)
        guard_worst = self._multiply_terms(M_worst, guard)
        body_avg    = self._create_sum(body.avg,   iter_var, "1", M_avg)
        body_worst  = self._create_sum(body.worst, iter_var, "1", M_worst)

        avg   = self._add_terms([guard_avg,  body_avg,  guard])
        worst = self._add_terms([guard_worst, body_worst, guard])

        cost = CostExpr(best=best, avg=avg, worst=worst)
        own  = CostExpr(best=guard, avg=self._add_terms([guard_avg, guard]),
                        worst=self._add_terms([guard_worst, guard]))
        ls, le, snippet = self._extract_line_info(while_stmt)
        self.costs.append(NodeCost(
            node_id=node_id, node_type="While",
            line_start=ls, line_end=le, code_snippet=snippet,
            cost=cost, own_cost=own
        ))
        return cost

    # ---- If ----
    def _analyze_if(self, if_stmt: If) -> CostExpr:
        node_id = self.context.next_id("If")
        guard = self._cost_of_expr(if_stmt.cond)
        then_c = self._analyze_block(if_stmt.then_block)
        else_c = self._analyze_block(if_stmt.else_block) if if_stmt.else_block else CostExpr(best="0", avg="0", worst="0")

        best  = self._add_terms([guard, self._min_cost(then_c.best, else_c.best)])
        p = str(self.DEFAULT_P_TRUE); q = str(1 - self.DEFAULT_P_TRUE)
        avg   = self._add_terms([guard, self._multiply_terms(p, then_c.avg), self._multiply_terms(q, else_c.avg)])
        worst = self._add_terms([guard, self._max_cost(then_c.worst, else_c.worst)])

        cost = CostExpr(best=best, avg=avg, worst=worst)
        ls, le, snippet = self._extract_line_info(if_stmt)
        self.costs.append(NodeCost(
            node_id=node_id, node_type="If",
            line_start=ls, line_end=le, code_snippet=snippet,
            cost=cost, own_cost=CostExpr(best=guard, avg=guard, worst=guard)
        ))
        return cost

    # ---- Assign / ExprStmt ----
    def _analyze_assign(self, assign: Assign) -> CostExpr:
        node_id = self.context.next_id("Assign")
        rhs = self._cost_of_expr(assign.value)
        total = self._add_terms(["1", rhs])
        cost = CostExpr(best=total, avg=total, worst=total)
        ls, le, snippet = self._extract_line_info(assign)
        self.costs.append(NodeCost(
            node_id=node_id, node_type="Assign",
            line_start=ls, line_end=le, code_snippet=snippet,
            cost=cost, own_cost=cost
        ))
        return cost

    def _analyze_expr_stmt(self, expr_stmt: ExprStmt) -> CostExpr:
        node_id = self.context.next_id("ExprStmt")
        ec = self._cost_of_expr(expr_stmt.expr) or "0"
        cost = CostExpr(best=ec, avg=ec, worst=ec)
        self.costs.append(NodeCost(node_id=node_id, node_type="ExprStmt", cost=cost))
        return cost

    # ---- Helpers de expresiones ----
    def _extract_line_info(self, stmt: Stmt) -> Tuple[int | None, int | None, str | None]:
        ls = getattr(stmt, 'line_start', None)
        le = getattr(stmt, 'line_end', None)
        snippet = None
        t = stmt.__class__.__name__
        if t == 'For' and hasattr(stmt, 'var'): snippet = f"for {stmt.var} ← ... to ..."
        elif t == 'While':  snippet = "while ..."
        elif t == 'If':     snippet = "if ..."
        elif t == 'Assign': snippet = f"{getattr(getattr(stmt, 'target', None), 'name', '...')} ← ..."
        elif t == 'Return': snippet = "return ..."
        return ls, le, snippet

    def _cost_of_expr(self, expr: Expr) -> str:
        if isinstance(expr, (Literal, Var)): return "0"
        if isinstance(expr, BinOp):
            return self._add_terms(["1", self._cost_of_expr(expr.left), self._cost_of_expr(expr.right)])
        if isinstance(expr, Compare):
            return self._add_terms(["1", self._cost_of_expr(expr.left), self._cost_of_expr(expr.right)])
        return "0"

    # ---- Utils algebra ----
    def _add_terms(self, terms: List[str]) -> str:
        nz = [t for t in terms if t and t != "0"]
        if not nz: return "0"
        if len(nz) == 1: return nz[0]
        return " + ".join(nz)

    def _multiply_terms(self, factor: str, expr: str) -> str:
        if factor == "0" or expr == "0": return "0"
        if factor == "1": return expr
        if expr == "1": return factor
        return f"{factor}*({expr})" if ("+" in expr or "-" in expr) else f"{factor}*{expr}"

    def _sum_costs(self, costs: List[CostExpr]) -> CostExpr:
        if not costs: return CostExpr(best="0", avg="0", worst="0")
        if len(costs) == 1: return costs[0]
        def join(xs):
            xs = [x for x in xs if x != "0"]
            return " + ".join(xs) if xs else "0"
        return CostExpr(
            best=join([c.best for c in costs]),
            avg=join([c.avg for c in costs]),
            worst=join([c.worst for c in costs]),
        )

    def _create_sum(self, inner: str, var: str, start: str, end: str) -> str:
        return "0" if inner == "0" else f"Sum({inner}, ({var}, {start}, {end}))"

    def _expr_to_str(self, expr: Expr) -> str:
        if isinstance(expr, Literal): return str(expr.value)
        if isinstance(expr, Var):     return expr.name
        if isinstance(expr, BinOp):   return f"({self._expr_to_str(expr.left)} {expr.op} {self._expr_to_str(expr.right)})"
        return "n"

    def _min_cost(self, a: str, b: str) -> str:
        if a == "0" or b == "0": return "0"
        return a if a == b else f"min({a}, {b})"

    def _max_cost(self, a: str, b: str) -> str:
        return a if a == b else f"max({a}, {b})"

    # ---- NUEVO: sumar costo total desde per_line ----
    def _sum_from_lines(self, per_line: List[LineCost]) -> CostExpr:
        best_terms = [lc.cost.best  for lc in per_line if lc.cost.best  != "0"]
        avg_terms  = [lc.cost.avg   for lc in per_line if lc.cost.avg   != "0"]
        worst_terms= [lc.cost.worst for lc in per_line if lc.cost.worst != "0"]
        return CostExpr(
            best=self._add_terms(best_terms) if best_terms else "0",
            avg=self._add_terms(avg_terms) if avg_terms else "0",
            worst=self._add_terms(worst_terms) if worst_terms else "0",
        )

    # ---- Coste por línea (MVP) ----
    def _generate_line_costs(self, source_code: str) -> List[LineCost]:
        if not source_code:
            return []
        lines = source_code.split('\n')

        for_nodes = [n for n in self.costs if n.node_type == "For" and n.loop_info and n.line_start and n.line_end]
        for_nodes.sort(key=lambda n: (n.line_start, -n.line_end))
        if_nodes = [n for n in self.costs if n.node_type == "If" and n.line_start and n.line_end]
        if_nodes.sort(key=lambda n: (n.line_start, -n.line_end))

        line_to_loops: Dict[int, List[Tuple[str, str, str]]] = {}
        for ln in range(1, len(lines) + 1):
            inside = []
            for fn in for_nodes:
                # DENTRO del for (excluye la línea del encabezado)
                if fn.line_start < ln <= fn.line_end:
                    inside.append((fn.loop_info.var, fn.loop_info.start, fn.loop_info.end))
            if inside:
                line_to_loops[ln] = inside

        line_to_if_depth: Dict[int, int] = {}
        for ln in range(1, len(lines) + 1):
            d = sum(1 for inf in if_nodes if inf.line_start < ln <= inf.line_end)
            if d > 0: line_to_if_depth[ln] = d

        line_costs_map: Dict[int, Dict[str, List[str]]] = {}
        for node in self.costs:
            if not node.line_start or node.node_type in ['Function', 'Program']:
                continue
            ln = node.line_start

            if node.node_type == 'For':
                if node.loop_info:
                    start, end = node.loop_info.start, node.loop_info.end
                    evals = self._simplify_expr(f"({end}) - ({start}) + 2")
                    loops = line_to_loops.get(ln, [])
                    best = avg = worst = self._wrap_in_sums(evals, loops) if loops else evals
                else:
                    best = avg = worst = "1"

            elif node.node_type == 'While':
                # FIX: envolver el costo del while con las sumas de bucles contenedores
                if node.own_cost:
                    base_b, base_a, base_w = node.own_cost.best, node.own_cost.avg, node.own_cost.worst
                    loops = line_to_loops.get(ln, [])
                    if loops:
                        best  = self._wrap_in_sums(base_b, loops)
                        avg   = self._wrap_in_sums(base_a, loops)
                        worst = self._wrap_in_sums(base_w, loops)
                    else:
                        best, avg, worst = base_b, base_a, base_w
                else:
                    best = avg = worst = "0"

            else:
                if not node.own_cost:
                    continue
                loops = line_to_loops.get(ln, [])
                if_depth = line_to_if_depth.get(ln, 0)
                base_b, base_a, base_w = node.own_cost.best, node.own_cost.avg, node.own_cost.worst
                if if_depth > 0:
                    base_b = "0"
                    prob = 0.5 ** if_depth
                    if base_a != "0": base_a = f"({prob} * ({base_a}))"
                if loops:
                    best = self._wrap_in_sums(base_b, loops)
                    avg  = self._wrap_in_sums(base_a, loops)
                    worst= self._wrap_in_sums(base_w, loops)
                else:
                    best, avg, worst = base_b, base_a, base_w

            line_costs_map.setdefault(ln, {"operations": [], "costs_best": [], "costs_avg": [], "costs_worst": []})
            line_costs_map[ln]["operations"].append(node.node_type)
            line_costs_map[ln]["costs_best"].append(best)
            line_costs_map[ln]["costs_avg"].append(avg)
            line_costs_map[ln]["costs_worst"].append(worst)

        result: List[LineCost] = []
        for ln in sorted(line_costs_map.keys()):
            if 1 <= ln <= len(lines):
                data = line_costs_map[ln]
                result.append(LineCost(
                    line_number=ln,
                    code=lines[ln - 1],
                    operations=data["operations"],
                    cost=CostExpr(
                        best=self._add_terms(data["costs_best"]),
                        avg=self._add_terms(data["costs_avg"]),
                        worst=self._add_terms(data["costs_worst"]),
                    ),
                ))
        return result

    def _wrap_in_sums(self, base: str, loops: List[Tuple[str, str, str]]) -> str:
        out = base
        for var, start, end in reversed(loops):
            out = self._create_sum(out, var, start, end)
        return out


class CostAnalyzerAgent:
    def __init__(self):
        self.analyzer = CostAnalyzer()

    def analyze(self, program: Program, source_code: str = "") -> CostsOut:
        return self.analyzer.analyze(program, source_code)

    def __call__(self, input_data: dict) -> dict:
        try:
            ast = input_data.get("ast")
            if not isinstance(ast, Program):
                raise ValueError("Input 'ast' debe ser Program")
            costs = self.analyze(ast, input_data.get("source_code", ""))
            return {"costs": costs, "success": True, "error": None}
        except Exception as e:
            return {"costs": None, "success": False, "error": str(e)}


# Singleton
_cost_analyzer: CostAnalyzerAgent | None = None

def get_cost_analyzer() -> CostAnalyzerAgent:
    global _cost_analyzer
    if _cost_analyzer is None:
        _cost_analyzer = CostAnalyzerAgent()
    return _cost_analyzer
