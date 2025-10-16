# Pine Script MCP Server Documentation

Comprehensive Pine Script development tools integrated with TradingViewMCPServer.

## Overview

The Pine Script MCP Server provides professional-grade development tools for Pine Script, including real-time syntax validation, intelligent code completion, version detection, code conversion, comprehensive documentation, and a testing sandbox.

## Features

### 1. Real-time Syntax Validation ✓

Validates Pine Script code before execution with detailed error reporting.

**Tool:** `validate_pine_script`

```python
# Example usage in Claude Desktop
validate_pine_script("""
//@version=5
indicator("My Indicator")
myMa = ta.sma(close, 20)
plot(myMa)
""")
```

**Features:**
- Syntax error detection (missing brackets, invalid operators)
- Function signature validation
- Parameter type checking
- Deprecated function warnings
- Version compatibility checks
- Line-by-line error reporting with suggestions

**Error Codes:**
- `E001`: Syntax error
- `E101`: Unknown function
- `E102`: Version compatibility error
- `E103`: Invalid function arguments
- `W101`: Deprecated function warning

### 2. Live Documentation Access 📚

Fetch comprehensive documentation for any Pine Script function or topic.

**Tool:** `get_pine_documentation`

```python
# Get function documentation
get_pine_documentation("ta.sma")

# Get topic documentation
get_pine_documentation("variables")
get_pine_documentation("operators")
```

**Provides:**
- Function signatures with all parameters
- Parameter types (series, simple, const, input)
- Return types
- Detailed descriptions
- Code examples
- Related functions
- Links to official TradingView docs

**Available Topics:**
- `variables` - Variable declarations and scoping
- `operators` - Arithmetic, comparison, logical operators
- `types` - Pine Script type system

### 3. Function Signature Checking ✓

Validates function calls with comprehensive parameter checking.

Built into `validate_pine_script` tool. Checks:
- Required vs optional parameters
- Parameter types (int, float, bool, color, string)
- Type qualifiers (series, simple, const, input)
- Named parameter validation
- Parameter count verification

### 4. Code Testing Sandbox 🧪

Safe environment for testing Pine Script code with validation and metrics.

**Tool:** `test_pine_script`

```python
test_pine_script(
    code="//@version=5\nindicator('Test')\nplot(ta.sma(close, 20))",
    symbol="AAPL",
    timeframe="1h",
    bars=100
)
```

**Features:**
- Syntax validation before execution
- Performance metrics
- Execution time tracking
- Error catching and reporting
- Simulated execution environment
- Test with different symbols and timeframes

**Note:** Full backtesting requires TradingView platform integration. This sandbox validates syntax and provides static analysis.

### 5. Error Explanations 💡

Get detailed, actionable explanations for Pine Script errors.

**Tool:** `explain_pine_error`

```python
explain_pine_error("E101", "Unknown function: sma")
```

**Provides:**
- Clear error description
- Common causes (multiple)
- Step-by-step solutions
- Before/after code examples
- Links to relevant documentation

**Error Database:**
- E001: Syntax errors
- E101: Unknown functions
- E102: Version compatibility
- E103: Invalid arguments
- W101: Deprecated functions
- TYPE_ERROR: Type mismatches

### 6. Version Detection & Auto-adaptation 🔍

Automatically detect Pine Script version and analyze compatibility.

**Tool:** `detect_pine_version`

```python
detect_pine_version("""
study("Old Indicator")
myMa = sma(close, 20)
plot(myMa)
""")
```

**Detection Methods:**
1. Version directive parsing (`//@version=5`)
2. Syntax analysis (v5 namespaces, v4 var keyword)
3. Function usage patterns

**Provides:**
- Detected version (v1-v5)
- Detection confidence (0-100%)
- Detection source (directive/syntax/functions)
- Compatibility issues
- Deprecated features list
- Upgrade suggestions

**Supported Versions:**
- Pine Script v1 (legacy)
- Pine Script v2 (legacy)
- Pine Script v3 (deprecated)
- Pine Script v4 (current)
- Pine Script v5 (latest)

### 7. Version Conversion 🔄

Automatically convert Pine Script code between versions.

**Tool:** `convert_pine_version`

```python
convert_pine_version(
    code='study("Test")\nplot(sma(close, 20))',
    target_version=5
)
```

**Automatic Conversions:**
- `study()` → `indicator()`
- `security()` → `request.security()`
- `sma()` → `ta.sma()`
- `ema()` → `ta.ema()`
- `rsi()` → `ta.rsi()`
- `macd()` → `ta.macd()`
- Math functions → `math.*` namespace
- String functions → `str.*` namespace
- All technical indicators → `ta.*` namespace

**Supported Migrations:**
- v3 → v4
- v4 → v5
- Auto-detects source version if not specified

**Returns:**
- Converted code
- List of changes made
- Warnings for manual review

### 8. Intelligent Autocomplete 🚀

Context-aware code completion with function signatures.

**Tool:** `autocomplete_pine`

```python
autocomplete_pine(
    code="indicator('Test')\nta.",
    cursor_position=23
)
```

**Features:**
- Function completions with signatures
- Parameter hints during typing
- Keyword completions
- Built-in variable suggestions
- Namespace-aware completions (ta., math., str.)
- Relevance scoring
- Documentation preview

**Completion Types:**
- Functions (with parameter placeholders)
- Keywords (if, for, while, var, etc.)
- Built-in variables (close, open, high, low, volume)
- Type qualifiers (series, simple, const, input)

### 9. Code Templates 📝

Ready-to-use Pine Script templates for common patterns.

**Tool:** `get_pine_template`

```python
get_pine_template("strategy")
```

**Available Templates:**

**Simple Indicator:**
```pine
//@version=5
indicator("My Indicator", overlay=true)

length = input.int(14, "Period", minval=1)
myValue = ta.sma(close, length)
plot(myValue, color=color.blue, linewidth=2)
```

**Trading Strategy:**
```pine
//@version=5
strategy("My Strategy", overlay=true, initial_capital=10000)

fastLength = input.int(12, "Fast MA Length")
slowLength = input.int(26, "Slow MA Length")

fastMa = ta.ema(close, fastLength)
slowMa = ta.ema(close, slowLength)

longCondition = ta.crossover(fastMa, slowMa)
shortCondition = ta.crossunder(fastMa, slowMa)

if longCondition
    strategy.entry("Long", strategy.long)
if shortCondition
    strategy.close("Long")

plot(fastMa, color=color.blue)
plot(slowMa, color=color.red)
```

**Overlay Indicator:**
```pine
//@version=5
indicator("Support/Resistance", overlay=true)

length = input.int(20, "Lookback Length")

resistance = ta.highest(high, length)
support = ta.lowest(low, length)

plot(resistance, color=color.red, linewidth=2)
plot(support, color=color.green, linewidth=2)
```

## Usage Examples

### Example 1: Validate Pine Script Code

```
Ask Claude:
"Validate this Pine Script code:
//@version=5
indicator('RSI')
myRsi = ta.rsi(close, 14)
plot(myRsi)"
```

**Response includes:**
- Validation status (pass/fail)
- Detected version
- Any errors with line numbers
- Warnings about deprecated features
- Suggestions for improvements

### Example 2: Convert v4 Code to v5

```
Ask Claude:
"Convert this Pine Script v4 code to v5:
study('My Indicator')
myMa = sma(close, 20)
myRsi = rsi(close, 14)
plot(myMa)"
```

**Response includes:**
- Converted code with v5 syntax
- List of all changes made
- Warnings for manual review
- Migration guide

### Example 3: Get Function Documentation

```
Ask Claude:
"Show me the documentation for ta.macd function"
```

**Response includes:**
- Function signature
- All parameters with types
- Return type
- Description
- Usage examples
- Related functions

### Example 4: Test Code in Sandbox

```
Ask Claude:
"Test this Pine Script code for AAPL on 1h timeframe:
//@version=5
indicator('MACD')
[macd, signal, hist] = ta.macd(close, 12, 26, 9)
plot(macd, color=color.blue)
plot(signal, color=color.red)"
```

**Response includes:**
- Validation results
- Execution metrics
- Any errors or warnings
- Performance statistics

## Technical Details

### Architecture

```
tradingview_mcp/
├── pine_script/
│   ├── __init__.py           # Module exports
│   ├── lexer.py              # Tokenization (500+ lines)
│   ├── parser.py             # AST generation (600+ lines)
│   ├── validator.py          # Syntax validation (200+ lines)
│   ├── signatures.py         # Function database (500+ lines)
│   ├── errors.py             # Error explanations (300+ lines)
│   ├── documentation.py      # Docs system (200+ lines)
│   ├── sandbox.py            # Testing environment (200+ lines)
│   ├── versions.py           # Version detection (400+ lines)
│   └── autocomplete.py       # Intelligent completion (300+ lines)
```

### Function Signature Database

Comprehensive database of 50+ Pine Script built-in functions:

**Technical Analysis (ta namespace):**
- ta.sma, ta.ema, ta.rma, ta.wma
- ta.rsi, ta.macd, ta.stoch
- ta.bb (Bollinger Bands)
- ta.atr (Average True Range)
- And more...

**Math Functions (math namespace):**
- math.abs, math.max, math.min
- math.round, math.floor, math.ceil
- Trigonometric functions

**String Functions (str namespace):**
- str.tostring, str.tonumber
- str.length

**Input Functions:**
- input.int, input.float, input.bool
- input.string, input.color

**Plotting Functions:**
- plot, plotshape, plotchar
- hline, fill, bgcolor

### Performance

- **Validation Speed:** <500ms for typical scripts
- **Cache TTL:** 3600s (1 hour) for documentation
- **Memory:** Lightweight, minimal overhead
- **Concurrency:** Supports concurrent requests

### Limitations

1. **Backtesting:** Full strategy backtesting requires TradingView platform
2. **Chart Rendering:** Visual chart output not available in sandbox
3. **Real-time Data:** Sandbox uses simulated execution
4. **Custom Libraries:** v5 library imports not fully supported yet

## Error Reference

### Common Errors and Solutions

**E001: Syntax Error**
- **Cause:** Invalid syntax, missing brackets, typos
- **Solution:** Check matching parentheses, brackets, quotes

**E101: Unknown Function**
- **Cause:** Misspelled function, missing namespace
- **Solution:** Add namespace (ta.sma not sma in v5)

**E102: Version Compatibility**
- **Cause:** Using v5 features in v4 code
- **Solution:** Add `//@version=5` or use v4 alternatives

**E103: Invalid Arguments**
- **Cause:** Wrong parameter types or count
- **Solution:** Check function documentation

**W101: Deprecated Function**
- **Cause:** Using old v4 function names
- **Solution:** Update to v5 namespaced functions

## Best Practices

1. **Always specify version:** Start scripts with `//@version=5`
2. **Use type annotations:** Help catch errors early
3. **Validate before running:** Use `validate_pine_script` before testing
4. **Check deprecations:** Update old code to v5
5. **Use templates:** Start with proven patterns
6. **Test incrementally:** Validate changes as you code

## Integration with Trading Tools

The Pine Script tools integrate seamlessly with the existing TradingView MCP Server:

- Use Pine Script to develop custom indicators
- Test on real market data (Forex, Stocks, Crypto)
- Combine with 20+ built-in technical indicators
- Validate strategies before deploying to TradingView

## Support

For issues or questions:
1. Check error explanations with `explain_pine_error`
2. Review function documentation with `get_pine_documentation`
3. See [CONTRIBUTING.md](CONTRIBUTING.md) for bug reports
4. Visit [TradingView Pine Script Docs](https://www.tradingview.com/pine-script-docs/)

## Version History

### v3.0.0 (Current)
- Complete Pine Script MCP integration
- 8 comprehensive MCP tools
- Support for Pine Script v1-v5
- Intelligent validation and conversion
- 3000+ lines of Pine Script tooling code

### v2.0.0
- Multi-asset trading support
- 20+ technical indicators
- Modular architecture

### v1.0.0
- Initial release
- Basic forex support
