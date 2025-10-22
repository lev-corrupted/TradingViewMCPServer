"""
Pine Script Validator

Validates Pine Script code for syntax errors, type errors, and semantic issues.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .lexer import PineScriptLexer
from .parser import FunctionCall, Identifier, ParseError, parse_pine_script
from .signatures import FunctionSignatureDB
from .versions import VersionDetector


@dataclass
class ValidationError:
    """Represents a validation error"""

    line: int
    column: int
    severity: str  # 'error', 'warning', 'info'
    message: str
    code: str  # Error code (e.g., 'E001')
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of code validation"""

    valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    info: List[ValidationError]
    version: Optional[int] = None


class PineScriptValidator:
    """
    Validates Pine Script code for errors.

    Checks:
    - Syntax errors
    - Function signature errors
    - Type errors
    - Deprecated function usage
    - Version compatibility
    """

    def __init__(self):
        self.sig_db = FunctionSignatureDB()
        self.version_detector = VersionDetector()

    def validate(
        self, code: str, target_version: Optional[int] = None
    ) -> ValidationResult:
        """
        Validate Pine Script code.

        Args:
            code: Pine Script source code
            target_version: Target version (auto-detected if None)

        Returns:
            ValidationResult with errors and warnings
        """
        errors: List[ValidationError] = []
        warnings: List[ValidationError] = []
        info: List[ValidationError] = []

        # Detect version
        version_info = self.version_detector.detect_version(code)
        detected_version = version_info.version

        if target_version is None:
            target_version = detected_version

        # Add version info
        if version_info.detected_from != "directive":
            info.append(
                ValidationError(
                    line=1,
                    column=1,
                    severity="info",
                    message=f"Pine Script version detected as v{detected_version} "
                    f"(confidence: {version_info.confidence:.0%}, from: {version_info.detected_from})",
                    code="I001",
                    suggestion="Add '//@version=5' directive at the top for explicit version.",
                )
            )

        # Add compatibility warnings
        for issue in version_info.compatibility_issues:
            warnings.append(
                ValidationError(
                    line=1,
                    column=1,
                    severity="warning",
                    message=issue,
                    code="W001",
                )
            )

        # Parse code
        try:
            lexer = PineScriptLexer(code)
            tokens = lexer.tokenize()

            # Validate tokens
            for token in tokens:
                # Check for potential issues
                pass

            # Parse into AST
            ast = parse_pine_script(code)

            # Validate AST
            ast_errors = self._validate_ast(ast, target_version)
            errors.extend(ast_errors)

        except ParseError as e:
            errors.append(
                ValidationError(
                    line=e.line,
                    column=e.column,
                    severity="error",
                    message=str(e),
                    code="E001",
                )
            )
        except SyntaxError as e:
            # Extract line/column if available
            error_msg = str(e)
            line, col = 1, 1
            if "line" in error_msg:
                import re

                match = re.search(r"line (\d+)", error_msg)
                if match:
                    line = int(match.group(1))
            errors.append(
                ValidationError(
                    line=line,
                    column=col,
                    severity="error",
                    message=error_msg,
                    code="E002",
                )
            )
        except Exception as e:
            errors.append(
                ValidationError(
                    line=1,
                    column=1,
                    severity="error",
                    message=f"Validation error: {str(e)}",
                    code="E999",
                )
            )

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            version=target_version,
        )

    def _validate_ast(self, ast: Any, version: int) -> List[ValidationError]:
        """Validate the AST for semantic errors"""
        errors = []

        # Walk the AST and validate function calls
        self._walk_ast(ast, errors, version)

        return errors

    def _walk_ast(self, node: Any, errors: List[ValidationError], version: int):
        """Recursively walk AST and validate"""
        if isinstance(node, FunctionCall):
            # Validate function call
            func_sig = self.sig_db.get_function(node.name)

            if not func_sig:
                errors.append(
                    ValidationError(
                        line=node.line,
                        column=node.column,
                        severity="error",
                        message=f"Unknown function: '{node.name}'",
                        code="E101",
                        suggestion=self._suggest_similar_function(node.name),
                    )
                )
            else:
                # Check if function is available in target version
                if func_sig.version > version:
                    errors.append(
                        ValidationError(
                            line=node.line,
                            column=node.column,
                            severity="error",
                            message=f"Function '{node.name}' requires Pine Script v{func_sig.version}, "
                            f"but target version is v{version}",
                            code="E102",
                        )
                    )

                # Check if function is deprecated
                if func_sig.deprecated:
                    errors.append(
                        ValidationError(
                            line=node.line,
                            column=node.column,
                            severity="warning",
                            message=f"Function '{node.name}' is deprecated",
                            code="W101",
                            suggestion=(
                                f"Use '{func_sig.replacement}' instead"
                                if func_sig.replacement
                                else None
                            ),
                        )
                    )

                # Validate arguments
                positional_args = [
                    arg.value for arg in node.arguments if arg.name is None
                ]
                named_args = {
                    arg.name: arg.value
                    for arg in node.arguments
                    if arg.name is not None
                }

                valid, arg_errors = self.sig_db.validate_call(
                    node.name,
                    positional_args,
                    named_args,
                )

                for error_msg in arg_errors:
                    errors.append(
                        ValidationError(
                            line=node.line,
                            column=node.column,
                            severity="error",
                            message=error_msg,
                            code="E103",
                        )
                    )

        # Recursively walk child nodes
        if hasattr(node, "__dict__"):
            for attr_value in node.__dict__.values():
                if isinstance(attr_value, list):
                    for item in attr_value:
                        if hasattr(item, "line"):  # AST node
                            self._walk_ast(item, errors, version)
                elif hasattr(attr_value, "line"):  # AST node
                    self._walk_ast(attr_value, errors, version)

    def _suggest_similar_function(self, function_name: str) -> Optional[str]:
        """Suggest similar function names"""
        all_funcs = [f.full_name for f in self.sig_db.functions.values()]

        # Simple similarity check
        similar = []
        for func in all_funcs:
            if (
                function_name.lower() in func.lower()
                or func.lower() in function_name.lower()
            ):
                similar.append(func)

        if similar:
            return f"Did you mean: {', '.join(similar[:3])}?"

        return None

    def quick_check(self, code: str) -> bool:
        """Quick syntax check without full validation"""
        try:
            lexer = PineScriptLexer(code)
            lexer.tokenize()
            parse_pine_script(code)
            return True
        except:
            return False
