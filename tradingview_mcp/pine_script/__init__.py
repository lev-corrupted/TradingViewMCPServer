"""
Pine Script MCP Module

Provides comprehensive Pine Script validation, documentation, testing, and tooling.

Features:
- Real-time syntax validation
- Live documentation access
- Function signature checking
- Code testing sandbox
- Error explanations
- Version detection and auto-adaptation (v1-v5)
- Version conversion
- Autocomplete support
"""

from .validator import PineScriptValidator
from .parser import PineScriptParser
from .documentation import PineDocumentation
from .sandbox import PineSandbox
from .signatures import FunctionSignatureDB
from .errors import ErrorExplainer
from .versions import VersionDetector, VersionConverter
from .autocomplete import PineAutocomplete

__all__ = [
    "PineScriptValidator",
    "PineScriptParser",
    "PineDocumentation",
    "PineSandbox",
    "FunctionSignatureDB",
    "ErrorExplainer",
    "VersionDetector",
    "VersionConverter",
    "PineAutocomplete",
]
