"""
Pine Script Version Detection and Conversion

Detects Pine Script version from code and provides version conversion utilities.
Supports Pine Script v1-v6.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .lexer import PineScriptLexer
from .parser import Program, parse_pine_script


@dataclass
class VersionInfo:
    """Information about detected Pine Script version"""

    version: int
    detected_from: str  # 'directive', 'syntax', 'functions'
    confidence: float  # 0.0 to 1.0
    compatibility_issues: List[str]
    deprecated_features: List[str]
    suggestions: List[str]


class VersionDetector:
    """
    Detects Pine Script version from code.

    Detection strategies:
    1. Version directive (//@version=5)
    2. Syntax analysis (v5 syntax features)
    3. Function usage (version-specific functions)
    """

    # Version-specific features
    V6_ONLY_FEATURES = {
        "struct",
        "enum",
    }

    V5_ONLY_FEATURES = {
        "import",
        "export",
        "method",
        "type",
        "request.security",
        "indicator",
        "library",
    }

    V4_FEATURES = {
        "var",
        "varip",
    }

    V3_DEPRECATED = {
        "study",
        "security",
    }

    # Function name changes across versions
    FUNCTION_RENAMES = {
        # v4 -> v5
        "study": "indicator",
        "security": "request.security",
        "rsi": "ta.rsi",
        "sma": "ta.sma",
        "ema": "ta.ema",
        "rma": "ta.rma",
        "wma": "ta.wma",
        "vwma": "ta.vwma",
        "macd": "ta.macd",
        "stoch": "ta.stoch",
        "bb": "ta.bb",
        "atr": "ta.atr",
        "highest": "ta.highest",
        "lowest": "ta.lowest",
        "stdev": "ta.stdev",
        "correlation": "ta.correlation",
        "change": "ta.change",
        "cross": "ta.cross",
        "crossover": "ta.crossover",
        "crossunder": "ta.crossunder",
        "valuewhen": "ta.valuewhen",
        "barssince": "ta.barssince",
        "abs": "math.abs",
        "acos": "math.acos",
        "asin": "math.asin",
        "atan": "math.atan",
        "ceil": "math.ceil",
        "cos": "math.cos",
        "exp": "math.exp",
        "floor": "math.floor",
        "log": "math.log",
        "log10": "math.log10",
        "max": "math.max",
        "min": "math.min",
        "pow": "math.pow",
        "round": "math.round",
        "sign": "math.sign",
        "sin": "math.sin",
        "sqrt": "math.sqrt",
        "tan": "math.tan",
        "tostring": "str.tostring",
        "tonumber": "str.tonumber",
    }

    def __init__(self):
        pass

    def detect_version(self, code: str) -> VersionInfo:
        """
        Detect Pine Script version from code.

        Args:
            code: Pine Script source code

        Returns:
            VersionInfo with detected version and metadata
        """
        # Strategy 1: Check for version directive
        version_directive = self._extract_version_directive(code)
        if version_directive:
            return VersionInfo(
                version=version_directive,
                detected_from="directive",
                confidence=1.0,
                compatibility_issues=[],
                deprecated_features=self._find_deprecated_features(
                    code, version_directive
                ),
                suggestions=self._generate_suggestions(code, version_directive),
            )

        # Strategy 2: Analyze syntax and function usage
        detected_version, confidence, evidence = self._analyze_code_features(code)

        return VersionInfo(
            version=detected_version,
            detected_from=evidence,
            confidence=confidence,
            compatibility_issues=self._find_compatibility_issues(
                code, detected_version
            ),
            deprecated_features=self._find_deprecated_features(code, detected_version),
            suggestions=self._generate_suggestions(code, detected_version),
        )

    def _extract_version_directive(self, code: str) -> Optional[int]:
        """Extract version from //@version= directive"""
        match = re.search(r"//\s*@version\s*=\s*(\d+)", code, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    def _analyze_code_features(self, code: str) -> Tuple[int, float, str]:
        """
        Analyze code to detect version based on features.

        Returns:
            (version, confidence, evidence)
        """
        code_lower = code.lower()

        # Check for v6 features
        v6_score = 0
        for feature in self.V6_ONLY_FEATURES:
            if re.search(rf"\b{re.escape(feature)}\b", code_lower):
                v6_score += 1

        if v6_score >= 1:
            return (6, 0.95, "syntax")

        # Check for v5 features
        v5_score = 0
        for feature in self.V5_ONLY_FEATURES:
            if re.search(rf"\b{re.escape(feature)}\b", code_lower):
                v5_score += 1

        # Check for namespaced functions (v5)
        if re.search(r"\b(ta|math|str|array|matrix|request)\.\w+", code):
            v5_score += 2

        if v5_score >= 2:
            return (5, 0.9, "syntax")

        # Check for v4 features
        v4_score = 0
        for feature in self.V4_FEATURES:
            if re.search(rf"\b{re.escape(feature)}\b", code_lower):
                v4_score += 1

        if v4_score >= 1:
            return (4, 0.8, "syntax")

        # Check for deprecated v3 syntax
        v3_score = 0
        for feature in self.V3_DEPRECATED:
            if re.search(rf"\b{re.escape(feature)}\b", code_lower):
                v3_score += 1

        if v3_score >= 1:
            return (3, 0.7, "functions")

        # Default to v6 if no clear indicators (v6 is latest)
        return (6, 0.5, "default")

    def _find_compatibility_issues(self, code: str, target_version: int) -> List[str]:
        """Find compatibility issues for the detected version"""
        issues = []

        if target_version >= 5:
            # Check for deprecated v4 function names
            for old_name, new_name in self.FUNCTION_RENAMES.items():
                if re.search(rf"\b{re.escape(old_name)}\s*\(", code):
                    issues.append(
                        f"Function '{old_name}()' is deprecated in v5. Use '{new_name}()' instead."
                    )

        if target_version >= 4:
            # Check for v3 issues
            if re.search(r"\bstudy\s*\(", code):
                issues.append(
                    "Function 'study()' should be replaced with 'indicator()' in v4+."
                )

        return issues

    def _find_deprecated_features(self, code: str, version: int) -> List[str]:
        """Find deprecated features in the code"""
        deprecated = []

        if version >= 5:
            # v5 deprecations
            deprecated_patterns = {
                "security": "Use 'request.security' instead",
                "study": "Use 'indicator' instead",
            }

            for pattern, message in deprecated_patterns.items():
                if re.search(rf"\b{re.escape(pattern)}\s*\(", code):
                    deprecated.append(f"'{pattern}()' is deprecated. {message}.")

        return deprecated

    def _generate_suggestions(self, code: str, version: int) -> List[str]:
        """Generate suggestions for improving the code"""
        suggestions = []

        if version < 6:
            suggestions.append(
                f"Consider upgrading to Pine Script v6 (latest) for best features and performance. "
                f"Add '//@version=6' at the top of your script."
            )

        if version < 5:
            suggestions.append(
                f"Consider upgrading to Pine Script v5 for better features and performance. "
                f"Add '//@version=5' at the top of your script."
            )

            # Count functions that should be namespaced
            non_namespaced = 0
            for old_name in self.FUNCTION_RENAMES.keys():
                if re.search(rf"\b{re.escape(old_name)}\s*\(", code):
                    non_namespaced += 1

            if non_namespaced > 3:
                suggestions.append(
                    f"You're using {non_namespaced} functions that have been moved to namespaces in v5. "
                    f"Consider using the version converter to update your code."
                )

        if version >= 5:
            # Check if still using old syntax
            if re.search(r"\bstudy\s*\(", code):
                suggestions.append("Replace 'study()' with 'indicator()' for v5+.")

            if re.search(r"\bsecurity\s*\(", code):
                suggestions.append(
                    "Replace 'security()' with 'request.security()' for v5+."
                )

        if version == 6:
            suggestions.append(
                "Pine Script v6 supports advanced features like type, enum, and map. "
                "Use 'type' for custom data structures and 'enum' for state management."
            )

        return suggestions


class VersionConverter:
    """
    Converts Pine Script code between versions.

    Currently supports:
    - v3 -> v4 conversion
    - v4 -> v5 conversion
    - v5 -> v6 conversion
    """

    def __init__(self):
        self.detector = VersionDetector()

    def convert(
        self,
        code: str,
        target_version: int,
        source_version: Optional[int] = None,
    ) -> Tuple[str, List[str], List[str]]:
        """
        Convert Pine Script code to target version.

        Args:
            code: Source code
            target_version: Target version (1-6)
            source_version: Source version (auto-detected if None)

        Returns:
            (converted_code, changes_made, warnings)
        """
        # Detect source version if not provided
        if source_version is None:
            version_info = self.detector.detect_version(code)
            source_version = version_info.version

        changes = []
        warnings = []

        converted_code = code

        # Handle version directive
        if not re.search(r"//\s*@version\s*=", converted_code):
            # Add version directive
            converted_code = f"//@version={target_version}\n{converted_code}"
            changes.append(f"Added version directive: //@version={target_version}")
        else:
            # Update existing version directive
            converted_code = re.sub(
                r"//\s*@version\s*=\s*\d+",
                f"//@version={target_version}",
                converted_code,
            )
            changes.append(f"Updated version directive to: //@version={target_version}")

        # Perform version-specific conversions
        if source_version < 6 and target_version >= 6:
            converted_code, v6_changes, v6_warnings = self._convert_to_v6(
                converted_code
            )
            changes.extend(v6_changes)
            warnings.extend(v6_warnings)

        if source_version < 5 and target_version >= 5:
            converted_code, v5_changes, v5_warnings = self._convert_to_v5(
                converted_code
            )
            changes.extend(v5_changes)
            warnings.extend(v5_warnings)

        if source_version < 4 and target_version >= 4:
            converted_code, v4_changes, v4_warnings = self._convert_to_v4(
                converted_code
            )
            changes.extend(v4_changes)
            warnings.extend(v4_warnings)

        return converted_code, changes, warnings

    def _convert_to_v5(self, code: str) -> Tuple[str, List[str], List[str]]:
        """Convert code to Pine Script v5"""
        changes = []
        warnings = []

        converted = code

        # Replace function names
        for old_name, new_name in VersionDetector.FUNCTION_RENAMES.items():
            pattern = rf"\b{re.escape(old_name)}\s*\("
            if re.search(pattern, converted):
                converted = re.sub(pattern, f"{new_name}(", converted)
                changes.append(f"Renamed '{old_name}()' to '{new_name}()'")

        # Replace study() with indicator()
        if "study(" in converted:
            converted = converted.replace("study(", "indicator(")
            changes.append("Replaced 'study()' with 'indicator()'")

        # Check for potential issues
        if "security(" in converted and "request.security(" not in converted:
            warnings.append(
                "Manual review needed: 'security()' usage detected. "
                "Ensure all parameters are correct for 'request.security()'."
            )

        return converted, changes, warnings

    def _convert_to_v6(self, code: str) -> Tuple[str, List[str], List[str]]:
        """Convert code to Pine Script v6"""
        changes = []
        warnings = []

        converted = code

        # v6 is mostly backward compatible with v5
        # Main additions are new features (type, enum, map) rather than breaking changes

        # Add informational changes
        if converted and not any(kw in converted for kw in ["type ", "enum ", "map."]):
            warnings.append(
                "Pine Script v6 adds support for 'type' (structs), 'enum', and 'map' collections. "
                "Consider using these new features for better code organization."
            )

        return converted, changes, warnings

    def _convert_to_v4(self, code: str) -> Tuple[str, List[str], List[str]]:
        """Convert code to Pine Script v4"""
        changes = []
        warnings = []

        converted = code

        # v3 to v4 conversions
        # Replace 'input' with proper input functions
        if re.search(r"\binput\s*\(\s*\d+", converted):
            warnings.append(
                "Manual review needed: 'input()' usage detected. "
                "Consider using 'input.int()', 'input.float()', etc. in v4."
            )

        return converted, changes, warnings

    def get_migration_guide(self, from_version: int, to_version: int) -> str:
        """
        Get a migration guide for upgrading between versions.

        Args:
            from_version: Source version
            to_version: Target version

        Returns:
            Markdown-formatted migration guide
        """
        guide = f"# Pine Script Migration Guide: v{from_version} → v{to_version}\n\n"

        if from_version < 6 and to_version >= 6:
            guide += """
## Upgrading to Pine Script v6

### Key Changes

1. **New Features**
   - `struct` keyword for custom data structures
   - `enum` keyword for enumeration types
   - Enhanced type system
   - Improved performance

2. **Best Practices**
   - Use struct for complex data organization
   - Leverage enums for state management
   - Take advantage of improved type inference

### Example

```pine
//@version=6
indicator("v6 Example")

// Define a struct
type TradeData
    float entry
    float stop
    float target

// Create instance
var myTrade = TradeData.new(close, close * 0.98, close * 1.05)
```
"""

        if from_version < 5 and to_version >= 5:
            guide += """
## Upgrading to Pine Script v5

### Key Changes

1. **Namespaced Functions**
   - Most technical analysis functions moved to `ta.*` namespace
   - Math functions moved to `math.*` namespace
   - String functions moved to `str.*` namespace
   - Array functions moved to `array.*` namespace

2. **Renamed Functions**
   - `study()` → `indicator()`
   - `security()` → `request.security()`

3. **New Features**
   - `import` and `export` for libraries
   - `method` keyword for custom methods
   - `type` keyword for custom types

### Example Conversion

```pine
// v4
//@version=4
study("My Indicator")
myRsi = rsi(close, 14)
myMa = sma(close, 20)
plot(myRsi)

// v5
//@version=5
indicator("My Indicator")
myRsi = ta.rsi(close, 14)
myMa = ta.sma(close, 20)
plot(myRsi)
```
"""

        if from_version < 4 and to_version >= 4:
            guide += """
## Upgrading to Pine Script v4

### Key Changes

1. **Variable Declarations**
   - Introduced `var` keyword for persistent variables
   - Introduced `varip` for intrabar persistence

2. **Type System**
   - Explicit type qualifiers: `series`, `simple`, `const`, `input`

3. **Input Functions**
   - Specific input functions: `input.int()`, `input.float()`, `input.bool()`
"""

        return guide
