"""
Pine Script Testing Sandbox

Provides a safe environment for testing Pine Script code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import time

from .validator import PineScriptValidator


@dataclass
class TestResult:
    """Result of code execution test"""
    success: bool
    output: Optional[str]
    errors: List[str]
    warnings: List[str]
    execution_time: float
    validation_passed: bool
    metrics: Dict[str, Any]


class PineSandbox:
    """
    Testing sandbox for Pine Script code.

    Features:
    - Syntax validation before execution
    - Simulated execution environment
    - Performance metrics
    - Error catching
    """

    def __init__(self):
        self.validator = PineScriptValidator()

    def test(
        self,
        code: str,
        symbol: str = "BTCUSD",
        timeframe: str = "1D",
        bars: int = 100,
    ) -> TestResult:
        """
        Test Pine Script code in sandbox.

        Args:
            code: Pine Script code to test
            symbol: Symbol to test with
            timeframe: Timeframe to test with
            bars: Number of bars to test

        Returns:
            TestResult with execution details
        """
        start_time = time.time()
        errors = []
        warnings = []
        output = None
        metrics = {}

        # Step 1: Validate syntax
        validation_result = self.validator.validate(code)

        if not validation_result.valid:
            errors.extend([e.message for e in validation_result.errors])
            return TestResult(
                success=False,
                output=None,
                errors=errors,
                warnings=[w.message for w in validation_result.warnings],
                execution_time=time.time() - start_time,
                validation_passed=False,
                metrics={},
            )

        # Step 2: Simulate execution
        # Note: Actual Pine Script execution requires TradingView API
        # This is a simulation for validation purposes

        try:
            # Collect metrics
            metrics = {
                "lines_of_code": len(code.split('\n')),
                "validation_time": time.time() - start_time,
                "symbol": symbol,
                "timeframe": timeframe,
                "bars_analyzed": bars,
                "version": validation_result.version,
            }

            output = f"""
Test Execution Summary:
- Symbol: {symbol}
- Timeframe: {timeframe}
- Bars: {bars}
- Pine Script Version: v{validation_result.version}
- Syntax: Valid ✓
- Lines of Code: {metrics['lines_of_code']}

Note: Full backtesting requires TradingView platform integration.
This sandbox validates syntax and provides static analysis.

Validation Warnings: {len(validation_result.warnings)}
"""

            if validation_result.warnings:
                output += "\nWarnings:\n"
                for warning in validation_result.warnings:
                    output += f"  - Line {warning.line}: {warning.message}\n"

            execution_time = time.time() - start_time

            return TestResult(
                success=True,
                output=output,
                errors=errors,
                warnings=[w.message for w in validation_result.warnings],
                execution_time=execution_time,
                validation_passed=True,
                metrics=metrics,
            )

        except Exception as e:
            errors.append(f"Execution error: {str(e)}")
            return TestResult(
                success=False,
                output=None,
                errors=errors,
                warnings=warnings,
                execution_time=time.time() - start_time,
                validation_passed=True,
                metrics=metrics,
            )

    def quick_test(self, code: str) -> bool:
        """Quick validation test without full execution"""
        return self.validator.quick_check(code)

    def get_test_template(self, indicator_type: str = "simple") -> str:
        """
        Get a test template for common indicator types.

        Args:
            indicator_type: Type of indicator ('simple', 'strategy', 'overlay')

        Returns:
            Template code
        """
        templates = {
            "simple": """
//@version=6
indicator("My Indicator", overlay=true)

// Input parameters
length = input.int(14, "Period", minval=1)

// Calculate indicator
myValue = ta.sma(close, length)

// Plot results
plot(myValue, color=color.blue, linewidth=2)
""",
            "strategy": """
//@version=6
strategy("My Strategy", overlay=true, initial_capital=10000, default_qty_type=strategy.fixed, default_qty_value=1)

// Input parameters
fastLength = input.int(12, "Fast MA Length")
slowLength = input.int(26, "Slow MA Length")

// Calculate indicators
fastMa = ta.ema(close, fastLength)
slowMa = ta.ema(close, slowLength)

// Strategy logic
longCondition = ta.crossover(fastMa, slowMa)
shortCondition = ta.crossunder(fastMa, slowMa)

// Execute trades
if longCondition
    strategy.entry("Long", strategy.long)
if shortCondition
    strategy.close("Long")

// Plot indicators
plot(fastMa, color=color.blue)
plot(slowMa, color=color.red)
""",
            "overlay": """
//@version=6
indicator("Support/Resistance", overlay=true)

// Input parameters
length = input.int(20, "Lookback Length")

// Calculate levels
resistance = ta.highest(high, length)
support = ta.lowest(low, length)

// Plot levels
plot(resistance, color=color.red, linewidth=2, title="Resistance")
plot(support, color=color.green, linewidth=2, title="Support")

// Fill area
fill(plot(resistance), plot(support), color=color.new(color.gray, 90))
""",
        }

        return templates.get(indicator_type, templates["simple"])
