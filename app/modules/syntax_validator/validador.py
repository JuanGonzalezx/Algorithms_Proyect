# app/modules/syntax_validator/agent.py
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

from lark import Lark, LarkError, UnexpectedInput
from app.shared.models import PseudocodeIn, SyntaxValidationResult, ErrorItem

logger = logging.getLogger(__name__)


class SyntaxValidatorAgent:
    """Valida la sintaxis del pseudocódigo usando Lark y aplica normalizaciones suaves."""

    def __init__(self) -> None:
        self.grammar_path = (
            Path(__file__).parent.parent.parent / "shared" / "grammar" / "grammar.lark"
        )
        self.parser: Lark | None = None
        self._load_grammar()

    def _load_grammar(self) -> None:
        if not self.grammar_path.exists():
            raise FileNotFoundError(f"No se encontró la gramática: {self.grammar_path}")
        with open(self.grammar_path, "r", encoding="utf-8") as f:
            grammar_text = f.read()

        last_err: Exception | None = None
        for start_symbol in ("start", "program"):
            try:
                self.parser = Lark(
                    grammar_text,
                    start=start_symbol,
                    parser="lalr",
                    propagate_positions=True,
                    maybe_placeholders=False,
                )
                logger.info(f"Gramática cargada (start='{start_symbol}')")
                return
            except LarkError as e:
                last_err = e

        raise last_err if last_err else RuntimeError("No fue posible inicializar el parser")

    def _normalize_code(self, code: str) -> Tuple[str, List[str]]:
        """Normaliza saltos de línea y espacios finales; no cambia operadores ni semántica."""
        norms: List[str] = []
        normalized = code.replace("\r\n", "\n")
        if normalized != code:
            norms.append("Saltos de línea normalizados (CRLF→LF)")

        lines = normalized.split("\n")
        trimmed = [ln.rstrip() for ln in lines]
        if trimmed != lines:
            norms.append("Espacios finales eliminados")
        normalized = "\n".join(trimmed)

        if normalized and not normalized.endswith("\n"):
            normalized += "\n"
            norms.append("Nueva línea añadida al final")
        return normalized, norms

    def _extract_error(self, error: UnexpectedInput, code: str) -> ErrorItem:
        """Construye un ErrorItem con línea/columna, regla esperada y contexto."""
        linea = getattr(error, "line", None)
        columna = getattr(error, "column", None)
        esperado = getattr(error, "expected", None)
        regla = f"Se esperaba: {', '.join(sorted(esperado))}" if esperado else None

        detalle = str(error)
        if hasattr(error, "get_context"):
            try:
                ctx = error.get_context(code)
                detalle = f"{detalle}\n\nContexto:\n{ctx}"
            except Exception:
                pass

        sugerencia = None
        s = str(error).lower()
        if "unexpected end-of-input" in s:
            sugerencia = "Fin de entrada inesperado. Revisa cierres de bloque (end-*) o ';'."
        elif "unexpected token" in s:
            sugerencia = "Token inesperado. Revisa la sintaxis cerca de la posición indicada."
        elif "no terminal matches" in s:
            sugerencia = "No coincide ninguna regla. Revisa la estructura del enunciado."

        return ErrorItem(
            linea=linea,
            columna=columna,
            regla=regla,
            detalle=detalle,
            sugerencia=sugerencia,
        )

    def validate(self, input_data: PseudocodeIn) -> SyntaxValidationResult:
        """Valida el pseudocódigo completo contra la gramática."""
        assert self.parser is not None, "Parser no inicializado"
        code = input_data.text

        codigo_norm, normalizaciones = self._normalize_code(code)
        era_valido = False
        errores: List[ErrorItem] = []
        hints = {
            "parser_engine": "lark-lalr",
            "language_hint": input_data.language_hint,
        }

        try:
            tree = self.parser.parse(codigo_norm)
            era_valido = True
            hints["parse_tree_nodes"] = sum(1 for _ in tree.iter_subtrees())
            logger.debug("Validación sintáctica exitosa")
        except UnexpectedInput as e:
            errores.append(self._extract_error(e, codigo_norm))
            logger.debug("Error de sintaxis capturado por Lark", exc_info=False)
        except LarkError as e:
            errores.append(
                ErrorItem(
                    detalle=str(e),
                    sugerencia="Error de parseo. Revisa la sintaxis del pseudocódigo.",
                )
            )
            logger.debug("Error general de Lark", exc_info=False)
        except Exception as e:
            errores.append(
                ErrorItem(
                    detalle=f"Error interno: {e}",
                    sugerencia="Error inesperado. Contacta al administrador.",
                )
            )
            logger.exception("Error inesperado en validate()")

        hints["total_errors"] = len(errores)
        hints["total_normalizations"] = len(normalizaciones)
        hints["code_length"] = len(codigo_norm)
        hints["line_count"] = codigo_norm.count("\n")

        return SyntaxValidationResult(
            era_algoritmo_valido=era_valido,
            codigo_corregido=codigo_norm,
            errores=errores,
            normalizaciones=normalizaciones,
            hints=hints,
        )

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Entrada/Salida compatible con el grafo (LangGraph)."""
        inp = state.get("input")
        if not isinstance(inp, PseudocodeIn):
            inp = PseudocodeIn(
                text=state.get("text", ""),
                language_hint=state.get("language_hint", "es"),
            )

        result = self.validate(inp)
        return {
            **state,
            "syntax_validation": result.model_dump(),
            "era_algoritmo_valido": result.era_algoritmo_valido,
            "codigo_corregido": result.codigo_corregido,
            "errores_sintaxis": result.errores,
            "normalizaciones": result.normalizaciones,
        }


# Singleton
_agent_instance: SyntaxValidatorAgent | None = None

def get_syntax_validator() -> SyntaxValidatorAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = SyntaxValidatorAgent()
    return _agent_instance
