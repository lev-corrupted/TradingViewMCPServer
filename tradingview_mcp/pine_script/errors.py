"""
Pine Script Error Explanation System

Provides detailed, human-readable explanations for Pine Script errors.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ErrorExplanation:
    """Detailed explanation of an error"""

    error_code: str
    title: str
    description: str
    causes: List[str]
    solutions: List[str]
    examples: List[str]
    related_docs: List[str]


class ErrorExplainer:
    """
    Explains Pine Script errors in detail.

    Provides context, causes, solutions, and examples.
    """

    def __init__(self):
        self.explanations: Dict[str, ErrorExplanation] = {}
        self._initialize_explanations()

    def _initialize_explanations(self):
        """Initialize error explanation database"""

        self.explanations["E001"] = ErrorExplanation(
            error_code="E001",
            title="Syntax Error",
            description="The Pine Script parser encountered invalid syntax.",
            causes=[
                "Missing or mismatched parentheses, brackets, or quotes",
                "Invalid operator usage",
                "Unexpected character or symbol",
                "Incorrect statement structure",
            ],
            solutions=[
                'Check for matching parentheses: ( ), brackets: [ ], and quotes: " "',
                "Verify operator syntax (e.g., == for equality, not =)",
                "Ensure proper statement structure (assignments, function calls, etc.)",
                "Look for typos or special characters in the wrong place",
            ],
            examples=[
                "// Incorrect\nplot(close\n\n// Correct\nplot(close)",
                "// Incorrect\nif close = 10\n\n// Correct\nif close == 10",
            ],
            related_docs=[
                "https://www.tradingview.com/pine-script-docs/language/Syntax",
            ],
        )

        self.explanations["E101"] = ErrorExplanation(
            error_code="E101",
            title="Unknown Function",
            description="The function you're trying to call doesn't exist in Pine Script.",
            causes=[
                "Function name misspelled",
                "Function doesn't exist in the current Pine Script version",
                "Missing namespace (e.g., ta., math., str.)",
                "User-defined function not declared",
            ],
            solutions=[
                "Check function name spelling",
                "Add proper namespace: ta.sma() instead of sma() in v5",
                "Verify the function exists in your Pine Script version",
                "Declare custom functions before calling them",
                "Check TradingView Pine Script documentation for available functions",
            ],
            examples=[
                "// v5 - Incorrect\nmyMa = sma(close, 20)\n\n// v5 - Correct\nmyMa = ta.sma(close, 20)",
                "// Incorrect\nresult = myCustomFunction(10)\n\n// Correct\nmyCustomFunction(x) =>\n    x * 2\nresult = myCustomFunction(10)",
            ],
            related_docs=[
                "https://www.tradingview.com/pine-script-docs/language/Built-ins",
            ],
        )

        self.explanations["E102"] = ErrorExplanation(
            error_code="E102",
            title="Version Compatibility Error",
            description="The function or feature you're using isn't available in the current Pine Script version.",
            causes=[
                "Using v5 features in v4 or earlier",
                "Missing //@version directive",
                "Function introduced in a later version",
            ],
            solutions=[
                "Add or update version directive: //@version=5",
                "Use version-appropriate alternatives",
                "Upgrade your script to the required version",
                "Check function availability in Pine Script docs",
            ],
            examples=[
                '// Add version directive\n//@version=5\nindicator("My Indicator")\nmyRsi = ta.rsi(close, 14)',
            ],
            related_docs=[
                "https://www.tradingview.com/pine-script-docs/language/Migration_guide",
            ],
        )

        self.explanations["E103"] = ErrorExplanation(
            error_code="E103",
            title="Invalid Function Arguments",
            description="The arguments provided to the function are incorrect.",
            causes=[
                "Wrong number of arguments",
                "Missing required arguments",
                "Invalid argument types",
                "Unknown named parameter",
            ],
            solutions=[
                "Check function documentation for required parameters",
                "Verify argument count and order",
                "Ensure argument types match expected types",
                "Use correct parameter names for named arguments",
            ],
            examples=[
                "// Incorrect - missing argument\nmyMa = ta.sma(close)\n\n// Correct\nmyMa = ta.sma(close, 20)",
                "// Incorrect - wrong parameter name\nplot(close, colour=color.red)\n\n// Correct\nplot(close, color=color.red)",
            ],
            related_docs=[
                "https://www.tradingview.com/pine-script-docs/language/Built-ins",
            ],
        )

        self.explanations["W101"] = ErrorExplanation(
            error_code="W101",
            title="Deprecated Function",
            description="You're using a function that has been deprecated in newer Pine Script versions.",
            causes=[
                "Using old v4 function names in v5",
                "Using study() instead of indicator()",
                "Using security() instead of request.security()",
            ],
            solutions=[
                "Replace with the recommended modern alternative",
                "Update to namespaced functions (ta., math., str.)",
                "Use indicator() instead of study()",
                "Consider upgrading to Pine Script v5",
            ],
            examples=[
                '// Deprecated (v4)\nstudy("My Indicator")\nmyMa = sma(close, 20)\n\n// Modern (v5)\nindicator("My Indicator")\nmyMa = ta.sma(close, 20)',
            ],
            related_docs=[
                "https://www.tradingview.com/pine-script-docs/language/Migration_guide",
            ],
        )

        self.explanations["TYPE_ERROR"] = ErrorExplanation(
            error_code="TYPE_ERROR",
            title="Type Mismatch",
            description="A value of one type is being used where a different type is expected.",
            causes=[
                "Passing string where number is expected",
                "Using series value where simple/const is required",
                "Incorrect type qualifier (series, simple, const, input)",
            ],
            solutions=[
                "Check argument types in function documentation",
                "Convert types explicitly (e.g., str.tonumber(), str.tostring())",
                "Use proper type qualifiers for variables",
                "Ensure input types match parameter expectations",
            ],
            examples=[
                '// Incorrect\nlength = "20"\nmyMa = ta.sma(close, length)\n\n// Correct\nlength = 20\nmyMa = ta.sma(close, length)',
            ],
            related_docs=[
                "https://www.tradingview.com/pine-script-docs/language/Type_system",
            ],
        )

    def explain(self, error_code: str, error_message: str = "") -> ErrorExplanation:
        """
        Get detailed explanation for an error.

        Args:
            error_code: Error code (e.g., 'E001')
            error_message: Original error message

        Returns:
            ErrorExplanation with details
        """
        explanation = self.explanations.get(error_code)

        if not explanation:
            # Return a generic explanation
            return ErrorExplanation(
                error_code=error_code,
                title="Unknown Error",
                description=error_message or "An unknown error occurred.",
                causes=["The specific cause is unknown."],
                solutions=[
                    "Check your Pine Script syntax",
                    "Review TradingView Pine Script documentation",
                    "Verify function names and parameters",
                ],
                examples=[],
                related_docs=["https://www.tradingview.com/pine-script-docs/"],
            )

        return explanation

    def format_explanation(self, explanation: ErrorExplanation) -> str:
        """Format error explanation as readable text"""
        output = f"# Error: {explanation.title} ({explanation.error_code})\n\n"
        output += f"{explanation.description}\n\n"

        output += "## Common Causes:\n"
        for i, cause in enumerate(explanation.causes, 1):
            output += f"{i}. {cause}\n"

        output += "\n## Solutions:\n"
        for i, solution in enumerate(explanation.solutions, 1):
            output += f"{i}. {solution}\n"

        if explanation.examples:
            output += "\n## Examples:\n"
            for example in explanation.examples:
                output += f"```pine\n{example}\n```\n\n"

        if explanation.related_docs:
            output += "\n## Related Documentation:\n"
            for doc in explanation.related_docs:
                output += f"- {doc}\n"

        return output
