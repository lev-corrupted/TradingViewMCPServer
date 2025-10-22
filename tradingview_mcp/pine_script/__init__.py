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

from .autocomplete import PineAutocomplete
from .documentation import PineDocumentation
from .errors import ErrorExplainer
from .parser import PineScriptParser
from .sandbox import PineSandbox
from .signatures import FunctionSignatureDB
from .validator import PineScriptValidator
from .versions import VersionConverter, VersionDetector

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
