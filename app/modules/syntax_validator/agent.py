"""
Agente de validación sintáctica para pseudocódigo.
Utiliza Lark para parsear y validar la sintaxis del pseudocódigo.
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, List
from lark import Lark, LarkError, UnexpectedInput, UnexpectedToken, UnexpectedCharacters
from lark.exceptions import VisitError

from app.shared.models import PseudocodeIn, SyntaxValidationResult, ErrorItem

logger = logging.getLogger(__name__)


class SyntaxValidatorAgent:
    """
    Agente responsable de validar la sintaxis del pseudocódigo usando Lark.
    """

    def __init__(self):
        """Inicializa el agente cargando la gramática Lark."""
        # Usar gramática compartida
        self.grammar_path = Path(__file__).parent.parent.parent / "shared" / "grammar" / "grammar.lark"
        self.parser = None
        self._load_grammar()

    def _load_grammar(self):
        """Carga la gramática Lark desde el archivo."""
        try:
            if not self.grammar_path.exists():
                raise FileNotFoundError(f"Archivo de gramática no encontrado: {self.grammar_path}")

            with open(self.grammar_path, "r", encoding="utf-8") as f:
                grammar_text = f.read()

            self.parser = Lark(
                grammar_text,
                start="start",
                parser="lalr",
                propagate_positions=True,
                maybe_placeholders=False
            )
            logger.info("Gramática cargada exitosamente")
        except Exception as e:
            logger.error(f"Error al cargar gramática: {e}")
            raise

    def _normalize_code(self, code: str) -> tuple[str, List[str]]:
        """
        Aplica normalizaciones básicas al código.
        
        Args:
            code: Código original
            
        Returns:
            Tupla (código_normalizado, lista_de_normalizaciones)
        """
        normalizations = []
        normalized = code

        # Normalizar saltos de línea
        if "\r\n" in normalized:
            normalized = normalized.replace("\r\n", "\n")
            normalizations.append("Saltos de línea normalizados (CRLF → LF)")

        # Eliminar espacios al final de las líneas
        lines = normalized.split("\n")
        trimmed_lines = [line.rstrip() for line in lines]
        if any(line != trimmed for line, trimmed in zip(lines, trimmed_lines)):
            normalized = "\n".join(trimmed_lines)
            normalizations.append("Espacios en blanco al final de líneas eliminados")

        # Asegurar que el archivo termine con nueva línea
        if normalized and not normalized.endswith("\n"):
            normalized += "\n"
            normalizations.append("Nueva línea añadida al final del archivo")

        # Normalizar símbolos de comparación comunes
        replacements = [
            ("<=", "≤"),
            (">=", "≥"),
            ("!=", "≠"),
        ]
        
        for old, new in replacements:
            if old in normalized:
                normalized = normalized.replace(old, new)
                normalizations.append(f"Operador '{old}' normalizado a '{new}'")

        return normalized, normalizations

    def _extract_error_details(self, error: LarkError, code: str) -> ErrorItem:
        """
        Extrae detalles del error de Lark y crea un ErrorItem.
        
        Args:
            error: Excepción de Lark
            code: Código que causó el error
            
        Returns:
            ErrorItem con detalles del error
        """
        linea = None
        columna = None
        detalle = str(error)
        regla = None
        sugerencia = None

        # Extraer información de posición
        if isinstance(error, (UnexpectedInput, UnexpectedToken, UnexpectedCharacters)):
            linea = getattr(error, "line", None)
            columna = getattr(error, "column", None)
            
            # Intentar extraer el token esperado
            if hasattr(error, "expected"):
                expected = error.expected
                if expected:
                    regla = f"Se esperaba: {', '.join(expected)}"
                    sugerencia = f"Verifica la sintaxis cerca de la línea {linea}"
            
            # Obtener contexto del error
            if hasattr(error, "get_context"):
                context = error.get_context(code)
                detalle = f"{detalle}\n\nContexto:\n{context}"

        # Sugerencias específicas basadas en el tipo de error
        if "Unexpected token" in detalle:
            sugerencia = "Token inesperado. Verifica que la sintaxis sea correcta."
        elif "Unexpected end-of-input" in detalle:
            sugerencia = "Fin de archivo inesperado. Puede faltar 'end' o algún cierre de bloque."
        elif "no terminal matches" in detalle.lower():
            sugerencia = "No se encontró una regla gramatical válida. Revisa la estructura del código."

        return ErrorItem(
            linea=linea,
            columna=columna,
            regla=regla,
            detalle=detalle,
            sugerencia=sugerencia
        )

    def validate(self, input_data: PseudocodeIn) -> SyntaxValidationResult:
        """
        Valida la sintaxis del pseudocódigo.
        
        Args:
            input_data: Datos de entrada con el pseudocódigo
            
        Returns:
            SyntaxValidationResult con el resultado de la validación
        """
        code = input_data.text
        errores = []
        
        # Aplicar normalizaciones
        codigo_normalizado, normalizaciones = self._normalize_code(code)
        
        # Intentar parsear
        era_valido = False
        hints = {
            "parser_engine": "lark-lalr",
            "grammar_version": "1.0",
            "language_hint": input_data.language_hint
        }

        try:
            tree = self.parser.parse(codigo_normalizado)
            era_valido = True
            hints["parse_tree_nodes"] = len(list(tree.iter_subtrees()))
            logger.info("Pseudocódigo validado exitosamente")
            
        except UnexpectedInput as e:
            logger.warning(f"Error de sintaxis (UnexpectedInput): {e}")
            error_item = self._extract_error_details(e, codigo_normalizado)
            errores.append(error_item)
            
        except UnexpectedToken as e:
            logger.warning(f"Error de sintaxis (UnexpectedToken): {e}")
            error_item = self._extract_error_details(e, codigo_normalizado)
            errores.append(error_item)
            
        except UnexpectedCharacters as e:
            logger.warning(f"Error de sintaxis (UnexpectedCharacters): {e}")
            error_item = self._extract_error_details(e, codigo_normalizado)
            errores.append(error_item)
            
        except LarkError as e:
            logger.warning(f"Error de Lark: {e}")
            error_item = ErrorItem(
                detalle=str(e),
                sugerencia="Error de parseo. Verifica la sintaxis del pseudocódigo."
            )
            errores.append(error_item)
            
        except Exception as e:
            logger.error(f"Error inesperado durante validación: {e}", exc_info=True)
            error_item = ErrorItem(
                detalle=f"Error interno: {str(e)}",
                sugerencia="Error inesperado. Contacta al administrador del sistema."
            )
            errores.append(error_item)

        # Añadir hints adicionales
        hints["total_errors"] = len(errores)
        hints["total_normalizations"] = len(normalizaciones)
        hints["code_length"] = len(codigo_normalizado)
        hints["line_count"] = codigo_normalizado.count("\n")

        return SyntaxValidationResult(
            era_algoritmo_valido=era_valido,
            codigo_corregido=codigo_normalizado,
            errores=errores,
            normalizaciones=normalizaciones,
            hints=hints
        )

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método para usar el agente en un grafo de LangGraph.
        
        Args:
            state: Estado actual del grafo
            
        Returns:
        Entendido. Necesito modificar el cálculo de exact para que incluya los costos de evaluación de For/While, de manera que coincida con el análisis por línea.
        
        El problema está en que exact se calcula desde costs.total, que viene del análisis por bloques (que NO incluye evaluaciones de loops). Necesito modificar el método solve para que calcule exact sumando TODAS las líneas (incluyendo For/While).
        
        Déjame modificar el solver:
        
        Read solver.py, lines 59 to 110
        
        Veo el problema. El método está calculando exact desde cost_expr (que viene de costs.total, el análisis por bloques). Necesito cambiarlo para que calcule exact desde la suma de todas las líneas (incluyendo For/While). Voy a modificar esto:
        
        solver.py+15-2
        Perfecto. Ahora el cálculo de exact se hace sumando TODAS las líneas (incluyendo For/While), lo que hará que coincida con el resultado del análisis por línea. Voy a esperar que el servidor recargue y probar:
        
        
        sleep 4 && timeout 40 python test/test_only_line_analysis.py 2>&1
        Todavía no coinciden. El servidor debe estar usando cache o no recargó. Déjame reiniciar completamente el servidor:
        
        
        ps aux | grep "[u]vicorn" | awk '{print $2}' | xargs kill -9 2>/dev/null; sleep 2 && python -m uvicorn main:app --reload --port 8000 > server_exact_fix.log 2>&1 & sleep 10 && echo "Server ready"
        
        timeout 40 python test/test_only_line_analysis.py 2>&1
        🎉 ¡PERFECTO! Ahora sí coinciden:
        
        Análisis por línea (best): T(n) = n**2 + n - 1
        Exact (best): n**2 + n - 1
        ✅ ¡COINCIDEN!
        
        Análisis por línea (avg): T(n) = (7*n**2 + n - 4)/4
        Exact (avg): (7*n**2 + n - 4)/4
        ✅ ¡COINCIDEN!
        
        Análisis por línea (worst): T(n) = (5*n**2 - n - 2)/2
        Exact (worst): (5*n**2 - n - 2)/2
        ✅ ¡COINCIDEN!
        
        Ahora el sistema funciona correctamente:
        
        ✅ Solo análisis por línea (no hay análisis por bloques)
        
            Estado actualizado con el resultado de la validación
        """
        # Extraer input del estado
        pseudocode_input = state.get("input")
        if not isinstance(pseudocode_input, PseudocodeIn):
            # Intentar construir desde el estado
            pseudocode_input = PseudocodeIn(
                text=state.get("text", ""),
                language_hint=state.get("language_hint", "es")
            )

        # Validar
        result = self.validate(pseudocode_input)

        # Actualizar estado
        return {
            **state,
            "syntax_validation": result.model_dump(),
            "era_algoritmo_valido": result.era_algoritmo_valido,
            "codigo_corregido": result.codigo_corregido,
            "errores_sintaxis": result.errores,
            "normalizaciones": result.normalizaciones,
        }


# Instancia singleton del agente
_agent_instance = None


def get_syntax_validator() -> SyntaxValidatorAgent:
    """
    Obtiene la instancia singleton del agente de validación sintáctica.
    
    Returns:
        SyntaxValidatorAgent: Instancia del agente
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = SyntaxValidatorAgent()
    return _agent_instance
