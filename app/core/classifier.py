import re
from typing import Tuple
from app.models.schemas import InputType

class InputClassifier:
    """Clasifica si el input es pseudocódigo o lenguaje natural"""
    
    # Palabras clave del pseudocódigo
    PSEUDOCODE_KEYWORDS = {
        'begin', 'end', 'for', 'to', 'do', 'while', 'repeat', 'until',
        'if', 'then', 'else', 'call', 'return', 'mod', 'div'
    }
    
    # Símbolos específicos del pseudocódigo
    PSEUDOCODE_SYMBOLS = ['🡨', '►', '┌', '┐', '└', '┘', '≤', '≥', '≠']
    
    def classify_input(self, content: str) -> Tuple[InputType, float]:
        """
        Clasifica el tipo de entrada y devuelve la confianza
        
        Args:
            content: Contenido a clasificar
            
        Returns:
            Tuple[InputType, float]: Tipo detectado y confianza (0-1)
        """
        content_lower = content.lower()
        content_clean = re.sub(r'\s+', ' ', content_lower.strip())
        
        # Calcular score de pseudocódigo
        pseudocode_score = self._calculate_pseudocode_score(content_clean, content)
        
        # Umbral para decidir
        threshold = 0.3
        
        if pseudocode_score >= threshold:
            return InputType.PSEUDOCODE, pseudocode_score
        else:
            return InputType.NATURAL_LANGUAGE, 1 - pseudocode_score
    
    def _calculate_pseudocode_score(self, content_lower: str, original_content: str) -> float:
        """Calcula score de qué tan probable es que sea pseudocódigo"""
        score = 0.0
        total_checks = 0
        
        # 1. Presencia de palabras clave (peso: 0.4)
        keyword_count = 0
        for keyword in self.PSEUDOCODE_KEYWORDS:
            if keyword in content_lower:
                keyword_count += 1
        
        keyword_score = min(keyword_count / 3, 1.0)  # Normalizar a 3 keywords max
        score += keyword_score * 0.4
        total_checks += 0.4
        
        # 2. Presencia de símbolos específicos (peso: 0.3)
        symbol_count = 0
        for symbol in self.PSEUDOCODE_SYMBOLS:
            if symbol in original_content:
                symbol_count += 1
        
        symbol_score = min(symbol_count / 2, 1.0)  # Normalizar a 2 símbolos max
        score += symbol_score * 0.3
        total_checks += 0.3
        
        # 3. Estructura de bloques begin/end (peso: 0.2)
        begin_count = content_lower.count('begin')
        end_count = content_lower.count('end')
        block_score = 0.0
        
        if begin_count > 0 and end_count > 0:
            # Puntuación alta si hay balance de begin/end
            balance = min(begin_count, end_count) / max(begin_count, end_count)
            block_score = balance
        
        score += block_score * 0.2
        total_checks += 0.2
        
        # 4. Patrones de asignación (peso: 0.1)
        assignment_patterns = [
            r'\w+\s*🡨\s*\w+',  # variable 🡨 valor
            r'\w+\s*=\s*\w+',   # variable = valor (alternativo)
        ]
        
        assignment_score = 0.0
        for pattern in assignment_patterns:
            if re.search(pattern, original_content):
                assignment_score = 1.0
                break
        
        score += assignment_score * 0.1
        total_checks += 0.1
        
        return score / total_checks if total_checks > 0 else 0.0

# Instancia global
input_classifier = InputClassifier()