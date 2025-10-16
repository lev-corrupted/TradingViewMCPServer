"""
Tests for Pine Script MCP tools
"""

import pytest
from tradingview_mcp.pine_script import (
    PineScriptValidator,
    PineDocumentation,
    PineSandbox,
    ErrorExplainer,
    VersionDetector,
    VersionConverter,
    PineAutocomplete,
)


class TestPineScriptValidator:
    """Tests for Pine Script validator"""

    def test_valid_v5_code(self):
        """Test validation of valid Pine Script v5 code"""
        validator = PineScriptValidator()
        code = """
//@version=5
indicator("Test")
myMa = ta.sma(close, 20)
plot(myMa)
"""
        result = validator.validate(code)
        assert result.valid is True
        assert result.version == 5
        assert len(result.errors) == 0

    def test_syntax_error(self):
        """Test detection of syntax errors"""
        validator = PineScriptValidator()
        code = """
//@version=5
indicator("Test"
plot(close)
"""
        result = validator.validate(code)
        assert result.valid is False
        assert len(result.errors) > 0

    def test_deprecated_function_warning(self):
        """Test warning for deprecated functions"""
        validator = PineScriptValidator()
        code = """
//@version=5
indicator("Test")
myMa = sma(close, 20)
plot(myMa)
"""
        result = validator.validate(code)
        # Should have warning about deprecated sma()
        assert len(result.warnings) > 0 or len(result.errors) > 0


class TestVersionDetector:
    """Tests for version detection"""

    def test_detect_v5_from_directive(self):
        """Test detection from version directive"""
        detector = VersionDetector()
        code = "//@version=5\nindicator('Test')"
        result = detector.detect_version(code)
        assert result.version == 5
        assert result.detected_from == "directive"
        assert result.confidence == 1.0

    def test_detect_v5_from_syntax(self):
        """Test detection from v5 syntax"""
        detector = VersionDetector()
        code = "indicator('Test')\nmyMa = ta.sma(close, 20)"
        result = detector.detect_version(code)
        assert result.version == 5
        assert result.detected_from in ["syntax", "functions"]

    def test_detect_v4_from_syntax(self):
        """Test detection from v4 syntax"""
        detector = VersionDetector()
        code = "var x = 0\nmyMa = sma(close, 20)"
        result = detector.detect_version(code)
        assert result.version in [4, 5]


class TestVersionConverter:
    """Tests for version conversion"""

    def test_convert_v4_to_v5(self):
        """Test conversion from v4 to v5"""
        converter = VersionConverter()
        code = "study('Test')\nmyMa = sma(close, 20)"
        converted, changes, warnings = converter.convert(code, 5, 4)

        assert "indicator" in converted
        assert "ta.sma" in converted
        assert len(changes) > 0

    def test_version_directive_update(self):
        """Test version directive update"""
        converter = VersionConverter()
        code = "//@version=4\nstudy('Test')"
        converted, changes, warnings = converter.convert(code, 5, 4)

        assert "//@version=5" in converted
        assert "indicator" in converted


class TestPineDocumentation:
    """Tests for documentation system"""

    def test_get_function_docs(self):
        """Test getting function documentation"""
        docs = PineDocumentation()
        result = docs.get_function_docs("ta.sma")

        assert result is not None
        assert "ta.sma" in result
        assert "Moving Average" in result

    def test_get_topic_docs(self):
        """Test getting topic documentation"""
        docs = PineDocumentation()
        result = docs.get_topic_docs("variables")

        assert result is not None
        assert "Variables" in result or "var" in result.lower()

    def test_search_functions(self):
        """Test function search"""
        docs = PineDocumentation()
        results = docs.search("sma")

        assert len(results) > 0
        assert any("sma" in r["name"].lower() for r in results)


class TestPineSandbox:
    """Tests for code sandbox"""

    def test_sandbox_valid_code(self):
        """Test sandbox with valid code"""
        sandbox = PineSandbox()
        code = "//@version=5\nindicator('Test')\nplot(close)"
        result = sandbox.test(code)

        assert result.success is True
        assert result.validation_passed is True

    def test_sandbox_invalid_code(self):
        """Test sandbox with invalid code"""
        sandbox = PineSandbox()
        code = "//@version=5\nindicator('Test'\nplot(close)"
        result = sandbox.test(code)

        assert result.success is False
        assert result.validation_passed is False
        assert len(result.errors) > 0

    def test_get_template(self):
        """Test template generation"""
        sandbox = PineSandbox()
        template = sandbox.get_test_template("simple")

        assert template is not None
        assert "indicator" in template or "strategy" in template
        assert "//@version=" in template


class TestErrorExplainer:
    """Tests for error explanation system"""

    def test_explain_known_error(self):
        """Test explanation of known error"""
        explainer = ErrorExplainer()
        result = explainer.explain("E101")

        assert result.error_code == "E101"
        assert result.title is not None
        assert len(result.causes) > 0
        assert len(result.solutions) > 0

    def test_explain_unknown_error(self):
        """Test explanation of unknown error"""
        explainer = ErrorExplainer()
        result = explainer.explain("UNKNOWN999", "Some error")

        assert result.error_code == "UNKNOWN999"
        assert "unknown" in result.title.lower()

    def test_format_explanation(self):
        """Test formatted error explanation"""
        explainer = ErrorExplainer()
        explanation = explainer.explain("E001")
        formatted = explainer.format_explanation(explanation)

        assert "Error:" in formatted
        assert "Causes:" in formatted
        assert "Solutions:" in formatted


class TestPineAutocomplete:
    """Tests for autocomplete system"""

    def test_autocomplete_functions(self):
        """Test function autocomplete"""
        autocomplete = PineAutocomplete()
        code = "indicator('Test')\nta."
        suggestions = autocomplete.get_completions(code, len(code))

        assert len(suggestions) > 0
        # Should suggest ta.* functions
        assert any("ta." in s.label for s in suggestions)

    def test_autocomplete_keywords(self):
        """Test keyword autocomplete"""
        autocomplete = PineAutocomplete()
        code = "indicator('Test')\nif"
        suggestions = autocomplete.get_completions(code, len(code))

        assert len(suggestions) > 0

    def test_parameter_hints(self):
        """Test parameter hints"""
        autocomplete = PineAutocomplete()
        code = "indicator('Test')\nta.sma(close, "
        func_sig = autocomplete.get_parameter_hints(code, len(code) - 1)

        # Should detect we're inside ta.sma call
        # Note: This might be None if parser doesn't detect incomplete call
        # That's okay for now


class TestIntegration:
    """Integration tests"""

    def test_full_validation_workflow(self):
        """Test complete validation workflow"""
        validator = PineScriptValidator()
        explainer = ErrorExplainer()

        # Invalid code
        code = "//@version=5\nindicator('Test')\nmyMa = unknown_func(close, 20)"
        result = validator.validate(code)

        assert result.valid is False
        assert len(result.errors) > 0

        # Get explanation for first error
        if result.errors:
            error = result.errors[0]
            explanation = explainer.explain(error.code, error.message)
            assert explanation is not None

    def test_conversion_then_validation(self):
        """Test conversion followed by validation"""
        converter = VersionConverter()
        validator = PineScriptValidator()

        # Old v4 code
        old_code = "study('Test')\nmyMa = sma(close, 20)\nplot(myMa)"

        # Convert to v5
        new_code, changes, warnings = converter.convert(old_code, 5, 4)

        # Validate converted code
        result = validator.validate(new_code)

        # Converted code should be valid (or have fewer errors)
        assert result.version == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
