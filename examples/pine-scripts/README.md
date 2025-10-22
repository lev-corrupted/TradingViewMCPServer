# TradingView Pine Script Strategies

This folder contains Pine Script strategies, indicators, and overlays developed using the TradingViewMCPServer Pine Script development tools.

## 📁 Folder Structure

```
TradingViewPineStrats/
├── indicators/      # Technical indicators
├── strategies/      # Trading strategies
├── overlays/        # Chart overlays (S/R, patterns, etc.)
├── examples/        # Example scripts for learning
└── README.md        # This file
```

## 🎯 Purpose

Store and organize your Pine Script code developed with Claude Code and the TradingViewMCPServer Pine Script tools.

## 📝 Usage

### 1. Creating New Scripts

Ask Claude to create strategies:
```
"Create a MACD crossover strategy with proper risk management"
"Build an RSI divergence indicator"
"Make a support/resistance overlay using pivot points"
```

### 2. Validating Scripts

All scripts can be validated using the Pine Script MCP tools:
```python
# Claude will automatically use:
validate_pine_script(code)
```

### 3. Testing Scripts

Test scripts in the sandbox before deploying:
```python
test_pine_script(code, symbol="AAPL", timeframe="1h")
```

## 🔧 Pine Script Tools Available

Via TradingViewMCPServer MCP tools:
- ✅ Real-time validation
- ✅ Version detection (v1-v6)
- ✅ Version conversion
- ✅ Function documentation
- ✅ Error explanations
- ✅ Code testing sandbox
- ✅ Intelligent autocomplete
- ✅ Code templates

## 📚 Resources

- **Pine Script Docs**: See [../PINE_SCRIPT.md](../PINE_SCRIPT.md)
- **TradingView Docs**: https://www.tradingview.com/pine-script-docs/
- **MCP Server Docs**: See [../README.md](../README.md)

## 🎓 Best Practices

### File Naming
- Use descriptive names: `macd_crossover_strategy.pine`
- Include version: `rsi_divergence_v6.pine`
- Use categories: `strategies/`, `indicators/`, `overlays/`

### Code Organization
```pine
//@version=6
// ============================================================================
// STRATEGY/INDICATOR NAME
// Description: Clear description of what it does
// Author: Your Name
// Version: 1.0
// Created: 2025-01-XX
// ============================================================================

strategy("Strategy Name", overlay=true, initial_capital=10000)

// ===== INPUTS =====
length = input.int(14, "Period", minval=1)

// ===== INDICATORS =====
myIndicator = ta.sma(close, length)

// ===== STRATEGY LOGIC =====
longCondition = ta.crossover(close, myIndicator)

if longCondition
    strategy.entry("Long", strategy.long)

// ===== VISUALIZATION =====
plot(myIndicator, color=color.blue)
```

### Documentation
- Add clear comments
- Document inputs
- Explain strategy logic
- Include usage notes

## 📊 Strategy Template

```pine
//@version=6
strategy("Template Strategy",
         overlay=true,
         initial_capital=10000,
         default_qty_type=strategy.percent_of_equity,
         default_qty_value=10,
         commission_type=strategy.commission.percent,
         commission_value=0.1)

// ===== INPUTS =====
fastLength = input.int(12, "Fast MA Length", minval=1)
slowLength = input.int(26, "Slow MA Length", minval=1)
riskPercent = input.float(2.0, "Risk %", minval=0.1, maxval=10)

// ===== INDICATORS =====
fastMa = ta.ema(close, fastLength)
slowMa = ta.ema(close, slowLength)

// ===== ENTRY CONDITIONS =====
longCondition = ta.crossover(fastMa, slowMa)
shortCondition = ta.crossunder(fastMa, slowMa)

// ===== RISK MANAGEMENT =====
atrValue = ta.atr(14)
stopLoss = 2 * atrValue
takeProfit = 3 * atrValue

// ===== EXECUTE TRADES =====
if longCondition
    strategy.entry("Long", strategy.long)
    strategy.exit("Long Exit", "Long", stop=close - stopLoss, limit=close + takeProfit)

if shortCondition
    strategy.entry("Short", strategy.short)
    strategy.exit("Short Exit", "Short", stop=close + stopLoss, limit=close - takeProfit)

// ===== VISUALIZATION =====
plot(fastMa, "Fast MA", color=color.blue, linewidth=2)
plot(slowMa, "Slow MA", color=color.red, linewidth=2)
plotshape(longCondition, "Long Signal", shape.triangleup, location.belowbar, color.green, size=size.small)
plotshape(shortCondition, "Short Signal", shape.triangledown, location.abovebar, color.red, size=size.small)
```

## 🚀 Quick Start

1. **Create a new strategy:**
   ```
   Ask Claude: "Create a new trend-following strategy using EMA crossovers"
   ```

2. **Validate the code:**
   ```
   Claude will automatically validate using validate_pine_script()
   ```

3. **Test it:**
   ```
   Ask Claude: "Test this strategy on SPY 1h timeframe"
   ```

4. **Save it:**
   ```
   Save to appropriate folder: strategies/, indicators/, or overlays/
   ```

5. **Deploy to TradingView:**
   - Copy the validated code
   - Open TradingView Pine Editor
   - Paste and apply to chart

## 📈 Example Strategies to Try

### Beginner
- Moving Average Crossover
- RSI Overbought/Oversold
- Bollinger Band Breakout

### Intermediate
- MACD + RSI Combo
- Support/Resistance Breakout
- Fibonacci Retracement Levels

### Advanced
- Multi-timeframe Analysis
- Custom Indicators with ML
- Portfolio Rebalancing

## ⚠️ Important Notes

### Backtesting
- Use TradingView's Strategy Tester for full backtesting
- The MCP sandbox provides syntax validation, not historical backtesting
- Always backtest on multiple symbols and timeframes

### Risk Management
- Always include stop losses
- Use proper position sizing
- Test with paper trading first
- Never risk more than 1-2% per trade

### Live Trading
- Thoroughly backtest all strategies
- Start with small position sizes
- Monitor performance regularly
- Adjust parameters as needed

## 🤝 Contributing

Feel free to:
- Share your successful strategies
- Improve existing code
- Add new examples
- Report issues

## 📞 Support

- **Pine Script Issues**: Use `explain_pine_error()` tool
- **Strategy Questions**: Ask Claude
- **Documentation**: See [PINE_SCRIPT.md](../PINE_SCRIPT.md)

---

**Happy Trading!** 📊🚀

*Remember: Past performance does not guarantee future results. Trade responsibly.*
