"""
Tests para el Series Solver.

Verifica que el solver:
1. Resuelva sumatorias correctamente
2. Simplifique expresiones algebraicas
3. Calcule Big-O correctamente
4. Maneje símbolos desconocidos
5. Calcule cotas asintóticas (Ω, Θ, O)
"""
import pytest
from app.modules.solver.solver import SeriesSolver, SeriesSolverAgent, get_series_solver
from app.shared.models import CostExpr, SolveOut


class TestSeriesSolver:
    """Tests para la clase SeriesSolver."""
    
    def setup_method(self):
        """Inicializa un solver para cada test."""
        self.solver = SeriesSolver()
    
    def test_simple_constant(self):
        """Test: Expresión constante -> O(1)."""
        cost = CostExpr(
            best="1",
            avg="1",
            worst="1"
        )
        
        result = self.solver.solve(cost)
        
        assert result.exact.best == "1"
        assert result.exact.avg == "1"
        assert result.exact.worst == "1"
        assert result.big_o.worst == "O(1)"
        assert result.bounds.theta == "Θ(1)"
    
    def test_simple_sum(self):
        """Test: Sum(1, (k, 1, n)) -> n."""
        cost = CostExpr(
            best="Sum(1, (k, 1, n))",
            avg="Sum(1, (k, 1, n))",
            worst="Sum(1, (k, 1, n))"
        )
        
        result = self.solver.solve(cost)
        
        # Sum(1, (k, 1, n)) = n
        assert "n" in result.exact.worst
        assert result.big_o.worst == "O(n)"
        assert result.bounds.big_o == "O(n)"
    
    def test_linear_with_constants(self):
        """Test: 1 + Sum(1, (k, 1, n)) + 1 -> n + 2."""
        cost = CostExpr(
            best="1 + Sum(1, (k, 1, n)) + 1",
            avg="1 + Sum(1, (k, 1, n)) + 1",
            worst="1 + Sum(1, (k, 1, n)) + 1"
        )
        
        result = self.solver.solve(cost)
        
        # Debe simplificar a n + 2
        assert "n" in result.exact.worst
        # Big-O debe ser O(n) (ignora constantes)
        assert result.big_o.worst == "O(n)"
    
    def test_quadratic_nested_sum(self):
        """Test: Sum(Sum(1, (j, 1, n)), (i, 1, n)) -> n²."""
        cost = CostExpr(
            best="Sum(Sum(1, (j, 1, n)), (i, 1, n))",
            avg="Sum(Sum(1, (j, 1, n)), (i, 1, n))",
            worst="Sum(Sum(1, (j, 1, n)), (i, 1, n))"
        )
        
        result = self.solver.solve(cost)
        
        # Sum anidada -> n²
        assert result.big_o.worst == "O(n**2)"
        assert result.bounds.theta == "Θ(n**2)"
    
    def test_bubble_sort_pattern(self):
        """Test: Patrón de bubble sort -> O(n²)."""
        cost = CostExpr(
            best="0",
            avg="Sum(Sum((1 + 1 + 1 + 0)/2, (k, 1, (n - i))), (k, 1, (n - 1)))",
            worst="Sum(Sum(max(1 + 1 + 1, 0), (k, 1, (n - i))), (k, 1, (n - 1)))"
        )
        
        result = self.solver.solve(cost)
        
        # Mejor caso: O(1)
        assert result.big_o.best == "O(1)"
        
        # Peor caso: O(n²)
        assert result.big_o.worst == "O(n**2)"
        
        # Omega (mejor caso)
        assert "Ω" in result.bounds.omega
        
        # Big-O (peor caso)
        assert "O" in result.bounds.big_o
    
    def test_if_with_max(self):
        """Test: max(a, b) se simplifica correctamente."""
        cost = CostExpr(
            best="0",
            avg="(1 + 0)/2",
            worst="max(1, 0)"
        )
        
        result = self.solver.solve(cost)
        
        # max(1, 0) = 1
        assert result.exact.worst == "1"
        assert result.big_o.worst == "O(1)"
    
    def test_while_best_worst(self):
        """Test: While con mejor caso 0, peor caso n."""
        cost = CostExpr(
            best="0",
            avg="Sum(1, (k, 1, n/2))",
            worst="Sum(1, (k, 1, n))"
        )
        
        result = self.solver.solve(cost)
        
        # Mejor caso: 0 -> O(1)
        assert result.exact.best == "0"
        assert result.big_o.best == "O(1)"
        
        # Peor caso: n -> O(n)
        assert result.big_o.worst == "O(n)"
        
        # Bounds
        assert "Ω(1)" in result.bounds.omega
        assert "O(n)" in result.bounds.big_o
    
    def test_algebraic_simplification(self):
        """Test: Simplificación algebraica (n² + 3n + 1)."""
        cost = CostExpr(
            best="n**2 + 3*n + 1",
            avg="n**2 + 3*n + 1",
            worst="n**2 + 3*n + 1"
        )
        
        result = self.solver.solve(cost)
        
        # Debe simplificar correctamente
        assert "n**2" in result.exact.worst or "n²" in result.exact.worst
        
        # Big-O debe extraer término dominante
        assert result.big_o.worst == "O(n**2)"
    
    def test_serialization(self):
        """Test: El resultado se puede serializar a JSON."""
        cost = CostExpr(
            best="1",
            avg="Sum(1, (k, 1, n))",
            worst="Sum(1, (k, 1, n))"
        )
        
        result = self.solver.solve(cost)
        
        # Debe ser serializable
        result_dict = result.model_dump()
        
        assert "exact" in result_dict
        assert "big_o" in result_dict
        assert "bounds" in result_dict
        assert "omega" in result_dict["bounds"]
        assert "theta" in result_dict["bounds"]
        assert "big_o" in result_dict["bounds"]


class TestSeriesSolverAgent:
    """Tests para SeriesSolverAgent."""
    
    def test_agent_solve(self):
        """Test: Agent.solve() funciona correctamente."""
        agent = SeriesSolverAgent()
        
        cost = CostExpr(
            best="1",
            avg="Sum(1, (k, 1, n))",
            worst="Sum(1, (k, 1, n))"
        )
        
        result = agent.solve(cost)
        
        assert isinstance(result, SolveOut)
        assert result.big_o.worst == "O(n)"
    
    def test_langgraph_interface(self):
        """Test: Interfaz LangGraph __call__() funciona."""
        agent = SeriesSolverAgent()
        
        cost = CostExpr(
            best="1",
            avg="Sum(1, (k, 1, n))",
            worst="Sum(1, (k, 1, n))"
        )
        
        state = {"costs": cost}
        result = agent(state)
        
        assert result["success"] is True
        assert result["error"] is None
        assert isinstance(result["solution"], SolveOut)
        assert result["solution"].big_o.worst == "O(n)"
    
    def test_singleton(self):
        """Test: get_series_solver() retorna singleton."""
        solver1 = get_series_solver()
        solver2 = get_series_solver()
        
        assert solver1 is solver2


class TestEdgeCases:
    """Tests para casos borde."""
    
    def setup_method(self):
        """Inicializa un solver para cada test."""
        self.solver = SeriesSolver()
    
    def test_zero_cost(self):
        """Test: Costo cero -> O(1)."""
        cost = CostExpr(best="0", avg="0", worst="0")
        result = self.solver.solve(cost)
        
        assert result.exact.worst == "0"
        assert result.big_o.worst == "O(1)"
    
    def test_empty_string(self):
        """Test: String vacío se maneja como 0."""
        cost = CostExpr(best="", avg="", worst="")
        result = self.solver.solve(cost)
        
        assert result.exact.worst == "0"
        assert result.big_o.worst == "O(1)"
    
    def test_complex_expression(self):
        """Test: Expresión compleja se resuelve."""
        cost = CostExpr(
            best="1",
            avg="1 + Sum(1 + Sum(1, (j, 1, i)), (i, 1, n))",
            worst="1 + Sum(1 + Sum(1, (j, 1, i)), (i, 1, n))"
        )
        
        result = self.solver.solve(cost)
        
        # Debe calcular Big-O correctamente
        assert "O(" in result.big_o.worst
        # Nested sum -> O(n²)
        assert result.big_o.worst == "O(n**2)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
