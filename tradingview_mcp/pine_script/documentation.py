"""
Pine Script Documentation System

Fetches and caches Pine Script documentation from TradingView.
"""

from __future__ import annotations

import time
from typing import Optional, Dict, List
from dataclasses import dataclass
import re

from .signatures import FunctionSignatureDB


@dataclass
class DocEntry:
    """Documentation entry"""
    title: str
    content: str
    url: str
    examples: List[str]
    related: List[str]
    last_updated: float


class PineDocumentation:
    """
    Provides access to Pine Script documentation.

    Features:
    - Local function signature documentation
    - Documentation caching
    - Search functionality
    - Context-aware documentation
    """

    BASE_URL = "https://www.tradingview.com/pine-script-docs"

    def __init__(self, cache_ttl: int = 3600):
        self.sig_db = FunctionSignatureDB()
        self.cache: Dict[str, DocEntry] = {}
        self.cache_ttl = cache_ttl
        self._initialize_local_docs()

    def _initialize_local_docs(self):
        """Initialize local documentation from function signatures"""
        for func_name, func_sig in self.sig_db.functions.items():
            doc_content = self.sig_db.get_function_help(func_name)
            if doc_content:
                self.cache[func_name] = DocEntry(
                    title=func_sig.full_name,
                    content=doc_content,
                    url=f"{self.BASE_URL}/language/Built-ins#{func_sig.full_name}",
                    examples=func_sig.examples,
                    related=[],
                    last_updated=time.time(),
                )

    def get_function_docs(self, function_name: str, version: int = 5) -> Optional[str]:
        """
        Get documentation for a function.

        Args:
            function_name: Function name (e.g., 'ta.sma', 'plot')
            version: Pine Script version

        Returns:
            Documentation string or None
        """
        # Check cache first
        if function_name in self.cache:
            doc = self.cache[function_name]
            # Check if cache is still valid
            if time.time() - doc.last_updated < self.cache_ttl:
                return doc.content

        # Get from function signature database
        func_sig = self.sig_db.get_function(function_name)
        if func_sig:
            return self.sig_db.get_function_help(function_name)

        return None

    def search(self, query: str, version: int = 5) -> List[Dict[str, str]]:
        """
        Search documentation.

        Args:
            query: Search query
            version: Pine Script version

        Returns:
            List of matching documentation entries
        """
        results = []
        query_lower = query.lower()

        for func_name, doc in self.cache.items():
            if (
                query_lower in func_name.lower()
                or query_lower in doc.content.lower()
                or query_lower in doc.title.lower()
            ):
                results.append({
                    "name": func_name,
                    "title": doc.title,
                    "preview": doc.content[:200] + "...",
                    "url": doc.url,
                })

        return results

    def get_topic_docs(self, topic: str) -> Optional[str]:
        """
        Get documentation for a topic.

        Args:
            topic: Topic name (e.g., 'variables', 'operators', 'types')

        Returns:
            Documentation content
        """
        topics = {
            "variables": """
# Variables in Pine Script

Variables store values that can be used later in your code.

## Declaration

```pine
// Simple declaration
myVar = close

// With var keyword (persistent)
var myPersistentVar = 0

// With varip keyword (intrabar persistent)
varip myIntrabarVar = 0
```

## Type Qualifiers

- **series**: Value can change bar-to-bar (default)
- **simple**: Value is constant within the script but can use series
- **const**: Compile-time constant
- **input**: Value comes from user input

## Examples

```pine
//@version=5
indicator("Variables Example")

// Declare variables
length = input.int(14, "Period")
var sum = 0.0
varip tickCount = 0

// Use variables
myMa = ta.sma(close, length)
plot(myMa)
```

[TradingView Documentation](https://www.tradingview.com/pine-script-docs/language/Variable_declarations)
""",
            "operators": """
# Operators in Pine Script

## Arithmetic Operators
- `+` Addition
- `-` Subtraction
- `*` Multiplication
- `/` Division
- `%` Modulo

## Comparison Operators
- `==` Equal to
- `!=` Not equal to
- `>` Greater than
- `<` Less than
- `>=` Greater than or equal
- `<=` Less than or equal

## Logical Operators
- `and` Logical AND
- `or` Logical OR
- `not` Logical NOT

## Assignment Operators
- `=` Assignment
- `:=` Reassignment
- `+=` Add and assign
- `-=` Subtract and assign
- `*=` Multiply and assign
- `/=` Divide and assign

## Ternary Operator
```pine
result = condition ? value_if_true : value_if_false
```

[TradingView Documentation](https://www.tradingview.com/pine-script-docs/language/Operators)
""",
            "types": """
# Type System in Pine Script

Pine Script has a strong type system with several built-in types.

## Basic Types
- **int**: Integer numbers (42, -10, 0)
- **float**: Floating-point numbers (3.14, -0.5)
- **bool**: Boolean values (true, false)
- **color**: Color values (color.red, #FF0000)
- **string**: Text strings ("Hello", 'World')

## Special Types
- **line**: Line drawings
- **label**: Text labels
- **box**: Box drawings
- **table**: Tables
- **array**: Arrays of values
- **matrix**: Matrices

## Type Qualifiers
- **series**: Values can change on each bar
- **simple**: Values are determined at bar zero
- **const**: Compile-time constants
- **input**: Values from inputs

[TradingView Documentation](https://www.tradingview.com/pine-script-docs/language/Type_system)
""",
        }

        return topics.get(topic.lower())

    def get_contextual_docs(self, code: str, cursor_position: int) -> Optional[str]:
        """
        Get context-aware documentation based on cursor position in code.

        Args:
            code: Full code
            cursor_position: Character position of cursor

        Returns:
            Relevant documentation
        """
        # Extract word at cursor position
        start = cursor_position
        end = cursor_position

        # Find word boundaries
        while start > 0 and (code[start - 1].isalnum() or code[start - 1] in '._'):
            start -= 1

        while end < len(code) and (code[end].isalnum() or code[end] in '._'):
            end += 1

        word = code[start:end]

        if not word:
            return None

        # Try to get function documentation
        return self.get_function_docs(word)

    def get_all_functions(self, namespace: Optional[str] = None, version: int = 5) -> List[str]:
        """
        Get list of all available functions.

        Args:
            namespace: Filter by namespace (e.g., 'ta', 'math')
            version: Pine Script version

        Returns:
            List of function names
        """
        functions = self.sig_db.get_all_functions(version)

        if namespace:
            functions = [f for f in functions if f.namespace == namespace]

        return [f.full_name for f in functions]
