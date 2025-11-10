"""
Módulo solver: resuelve sumatorias y calcula cotas asintóticas.

Exports:
    SeriesSolver: Clase principal para resolver expresiones de costo.
    SeriesSolverAgent: Wrapper con interfaz LangGraph.
    get_series_solver: Función para obtener instancia singleton del solver.
"""
from app.modules.solver.solver import SeriesSolver, SeriesSolverAgent, get_series_solver

__all__ = ["SeriesSolver", "SeriesSolverAgent", "get_series_solver"]
