"""
Pine Script Autocomplete System

Provides intelligent autocomplete suggestions for Pine Script code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import re

from .signatures import FunctionSignatureDB, FunctionSignature
from .lexer import KEYWORDS, BUILTIN_FUNCTIONS, TYPE_QUALIFIERS


@dataclass
class AutocompleteItem:
    """Autocomplete suggestion item"""
    label: str
    kind: str  # 'function', 'keyword', 'variable', 'type'
    detail: str
    documentation: Optional[str]
    insert_text: str
    score: float  # Relevance score


class PineAutocomplete:
    """
    Provides autocomplete suggestions for Pine Script.

    Features:
    - Function completion with signatures
    - Keyword completion
    - Context-aware suggestions
    - Parameter hints
    """

    def __init__(self):
        self.sig_db = FunctionSignatureDB()

    def get_completions(
        self,
        code: str,
        cursor_position: int,
        context: Optional[str] = None,
    ) -> List[AutocompleteItem]:
        """
        Get autocomplete suggestions.

        Args:
            code: Current code
            cursor_position: Cursor position in code
            context: Additional context

        Returns:
            List of autocomplete items
        """
        # Extract current word being typed
        current_word = self._extract_current_word(code, cursor_position)

        suggestions = []

        # Detect context
        is_after_dot = self._is_after_dot(code, cursor_position)

        if is_after_dot:
            # Namespace completion
            namespace = self._get_namespace(code, cursor_position)
            suggestions = self._get_namespace_completions(namespace, current_word)
        else:
            # General completions
            suggestions.extend(self._get_function_completions(current_word))
            suggestions.extend(self._get_keyword_completions(current_word))
            suggestions.extend(self._get_builtin_completions(current_word))

        # Sort by relevance
        suggestions.sort(key=lambda x: x.score, reverse=True)

        return suggestions[:50]  # Limit to top 50

    def _extract_current_word(self, code: str, cursor_position: int) -> str:
        """Extract the word currently being typed"""
        # Bounds checking
        if not code or cursor_position > len(code):
            return ""

        cursor_position = min(cursor_position, len(code))
        start = cursor_position

        # Find start of word
        while start > 0 and start <= len(code) and (code[start - 1].isalnum() or code[start - 1] in '_.'):
            start -= 1

        return code[start:cursor_position].lower()

    def _is_after_dot(self, code: str, cursor_position: int) -> bool:
        """Check if cursor is after a dot (namespace access)"""
        if not code or cursor_position == 0 or cursor_position > len(code):
            return False

        cursor_position = min(cursor_position, len(code))

        # Look backwards for dot
        i = cursor_position - 1
        while i >= 0 and i < len(code) and code[i] in ' \t':
            i -= 1

        if i >= 0 and i < len(code) and code[i].isalnum():
            # Continue backwards through identifier
            while i >= 0 and i < len(code) and (code[i].isalnum() or code[i] == '_'):
                i -= 1
            if i >= 0 and i < len(code) and code[i] == '.':
                return True

        return False

    def _get_namespace(self, code: str, cursor_position: int) -> Optional[str]:
        """Get the namespace before the dot"""
        if not code or cursor_position == 0 or cursor_position > len(code):
            return None

        cursor_position = min(cursor_position, len(code))

        # Look backwards for identifier.
        i = cursor_position - 1
        while i >= 0 and i < len(code) and code[i] in ' \t':
            i -= 1

        # Extract current partial word after dot
        while i >= 0 and i < len(code) and code[i].isalnum():
            i -= 1

        if i < 0 or i >= len(code) or code[i] != '.':
            return None

        # Extract namespace before dot
        dot_pos = i
        i -= 1
        while i >= 0 and i < len(code) and (code[i].isalnum() or code[i] == '_'):
            i -= 1

        namespace = code[i + 1:dot_pos]
        return namespace if namespace else None

    def _get_namespace_completions(
        self,
        namespace: Optional[str],
        prefix: str,
    ) -> List[AutocompleteItem]:
        """Get completions for a specific namespace"""
        if not namespace:
            return []

        suggestions = []

        # Get functions in namespace
        for func_name, func_sig in self.sig_db.functions.items():
            if func_sig.namespace == namespace:
                if prefix and not func_sig.name.lower().startswith(prefix):
                    continue

                suggestions.append(self._create_function_item(func_sig))

        return suggestions

    def _get_function_completions(self, prefix: str) -> List[AutocompleteItem]:
        """Get function completions"""
        suggestions = []

        for func_name, func_sig in self.sig_db.functions.items():
            full_name = func_sig.full_name.lower()
            name = func_sig.name.lower()

            if prefix and not (full_name.startswith(prefix) or name.startswith(prefix)):
                continue

            suggestions.append(self._create_function_item(func_sig))

        return suggestions

    def _get_keyword_completions(self, prefix: str) -> List[AutocompleteItem]:
        """Get keyword completions"""
        suggestions = []

        for keyword in KEYWORDS:
            if prefix and not keyword.startswith(prefix):
                continue

            suggestions.append(AutocompleteItem(
                label=keyword,
                kind='keyword',
                detail='keyword',
                documentation=f"Pine Script keyword: {keyword}",
                insert_text=keyword,
                score=0.7,
            ))

        return suggestions

    def _get_builtin_completions(self, prefix: str) -> List[AutocompleteItem]:
        """Get built-in variable completions"""
        builtins = ['close', 'open', 'high', 'low', 'volume', 'time', 'bar_index']

        suggestions = []

        for builtin in builtins:
            if prefix and not builtin.startswith(prefix):
                continue

            suggestions.append(AutocompleteItem(
                label=builtin,
                kind='variable',
                detail='built-in variable',
                documentation=f"Built-in Pine Script variable: {builtin}",
                insert_text=builtin,
                score=0.8,
            ))

        return suggestions

    def _create_function_item(self, func_sig: FunctionSignature) -> AutocompleteItem:
        """Create autocomplete item from function signature"""
        # Create parameter list
        params = []
        for param in func_sig.parameters:
            if param.optional:
                params.append(f"[{param.name}]")
            else:
                params.append(param.name)

        param_list = ", ".join(params)

        # Create insert text with placeholders
        insert_params = []
        for i, param in enumerate(func_sig.parameters, 1):
            if not param.optional:
                insert_params.append(f"${{{i}:{param.name}}}")

        insert_text = f"{func_sig.name}({', '.join(insert_params)})"

        score = 0.9
        if func_sig.deprecated:
            score = 0.3

        return AutocompleteItem(
            label=func_sig.full_name,
            kind='function',
            detail=f"({param_list}) → {func_sig.return_type.value}",
            documentation=func_sig.description,
            insert_text=insert_text,
            score=score,
        )

    def get_parameter_hints(
        self,
        code: str,
        cursor_position: int,
    ) -> Optional[FunctionSignature]:
        """
        Get parameter hints for function at cursor.

        Args:
            code: Current code
            cursor_position: Cursor position

        Returns:
            Function signature or None
        """
        # Find function call context
        func_name = self._find_function_context(code, cursor_position)

        if not func_name:
            return None

        return self.sig_db.get_function(func_name)

    def _find_function_context(self, code: str, cursor_position: int) -> Optional[str]:
        """Find which function call the cursor is inside"""
        if not code or cursor_position == 0 or cursor_position > len(code):
            return None

        cursor_position = min(cursor_position, len(code))

        # Look backwards for opening parenthesis
        paren_count = 0
        i = cursor_position - 1

        while i >= 0 and i < len(code):
            if code[i] == ')':
                paren_count += 1
            elif code[i] == '(':
                if paren_count == 0:
                    # Found the opening paren, now find function name
                    i -= 1
                    while i >= 0 and i < len(code) and code[i] in ' \t':
                        i -= 1

                    # Extract function name
                    end = i + 1
                    while i >= 0 and i < len(code) and (code[i].isalnum() or code[i] in '_.'):
                        i -= 1

                    func_name = code[i + 1:end]
                    return func_name if func_name else None
                else:
                    paren_count -= 1
            i -= 1

        return None
