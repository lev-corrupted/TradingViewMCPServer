# TradingView Integration Tools

**Compare your Python backtests with TradingView to validate accuracy**

---

## Quick Start

```bash
# Activate environment
source .venv/bin/activate

# 1. Compare data sources
python tradingview_integration/download_tradingview_data.py

# 2. Run Python backtest and get comparison parameters
python tradingview_integration/compare_strategies.py

# 3. After testing in TradingView, analyze differences
python tradingview_integration/analyze_differences.py
```

---

## Setup MCP Server (Optional)

This enables Claude Desktop to access TradingView data directly.

### Step 1: TradingView MCP is Already Installed

✅ Installed at: `~/TradingViewMCP/tradingview-mcp`

### Step 2: Configure Claude Desktop

1. Open config file:
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

2. Add this configuration:
```json
{
  "mcpServers": {
    "tradingview-data": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "src/tradingview_mcp/server.py"
      ],
      "cwd": "/Users/levtheswag/TradingViewMCP/tradingview-mcp"
    }
  }
}
```

3. Save (Ctrl+X, Y, Enter) and restart Claude Desktop (Cmd+Q)

4. Look for 🔌 icon in Claude Desktop to verify connection

### Step 3: Use in Claude Desktop

Once connected, you can ask Claude:
- "Show me top 10 volatile forex pairs right now"
- "Get EUR/USD technical indicators from TradingView"
- "Which crypto pairs have RSI above 70 on Binance?"

---

## Script Details

### 1. download_tradingview_data.py

**What it does:** Compares current prices between TradingView and yfinance

**Usage:**
```bash
python tradingview_integration/download_tradingview_data.py
```

**Output:**
- TradingView current price, RSI, and recommendation
- yfinance latest close price
- Price difference percentage

**Example:**
```
DATA COMPARISON: TradingView vs yfinance - EURUSD
✅ TradingView Current Price: $1.17240
   RSI: 50.26
✅ yfinance Latest Close: $1.17275
Price Difference: $0.00035 (0.029%)
✅ Data sources match closely!
```

---

### 2. compare_strategies.py

**What it does:** Runs a Python backtest and provides exact parameters for TradingView comparison

**Usage:**
```bash
python tradingview_integration/compare_strategies.py
```

**Output:**
- Python backtest results
- Exact parameters to use in TradingView
- CSV file with results

**Next Steps:**
1. Note the Fast MA (10) and Slow MA (20) parameters
2. Open TradingView
3. Create Pine Script strategy with same parameters
4. Run backtest on same date range
5. Compare results

---

### 3. analyze_differences.py

**What it does:** Interactive comparison tool for Python vs TradingView results

**Usage:**
```bash
python tradingview_integration/analyze_differences.py
```

**Process:**
1. Enter Python backtest results (Return %, Trades, Win Rate, Sharpe)
2. Enter TradingView backtest results
3. Get analysis of differences

**Expected Results:**
- Return difference < 2% = EXCELLENT
- Return difference < 5% = ACCEPTABLE
- Return difference > 5% = Investigate

---

## Validation Workflow

### Step 1: Test Data Accuracy
```bash
python tradingview_integration/download_tradingview_data.py
```
Verify yfinance data matches TradingView (should be < 0.1% difference)

### Step 2: Run Python Backtest
```bash
python tradingview_integration/compare_strategies.py
```
Note the results and parameters

### Step 3: Create TradingView Strategy

**Pine Script Template:**
```pinescript
//@version=5
strategy("MA Crossover", overlay=true)

fast = input.int(10, "Fast MA")
slow = input.int(20, "Slow MA")

fastMA = ta.sma(close, fast)
slowMA = ta.sma(close, slow)

if ta.crossover(fastMA, slowMA)
    strategy.entry("Long", strategy.long)

if ta.crossunder(fastMA, slowMA)
    strategy.close("Long")

plot(fastMA, color=color.blue)
plot(slowMA, color=color.red)
```

### Step 4: Compare Results
```bash
python tradingview_integration/analyze_differences.py
```

**Acceptable Differences:**
- 1-3% due to spread modeling
- Different timestamps (bar close times)
- Commission differences

---

## Troubleshooting

### TradingView Data Not Loading

**Problem:** `download_tradingview_data.py` returns no data

**Solutions:**
- Check internet connection
- TradingView API may be temporarily unavailable
- Try again in a few minutes

### Large Result Differences (>5%)

**Possible Causes:**
1. **Different data sources** - Check with `download_tradingview_data.py`
2. **Different spreads** - TradingView may use different commission
3. **Bar alignment** - TradingView may close bars at different times
4. **Trade execution** - Different execution logic

**Debug Steps:**
```bash
# Check data alignment
python tradingview_integration/download_tradingview_data.py

# Check Python backtest details
python tradingview_integration/compare_strategies.py

# Review individual trades in both systems
```

### MCP Server Not Connecting

**Check config:**
```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Verify path:**
```bash
ls ~/TradingViewMCP/tradingview-mcp/src/tradingview_mcp/server.py
```

**Restart Claude:**
```bash
pkill -9 "Claude"
open -a "Claude"
```

---

## Results Comparison Examples

### Example 1: Excellent Match ✅
```
Python:     Return: 12.5%, Trades: 45, Win Rate: 52%
TradingView: Return: 12.1%, Trades: 44, Win Rate: 50%

Difference: 0.4% return, 1 trade, 2% win rate
Verdict: EXCELLENT - Systems match closely!
```

### Example 2: Acceptable Difference ⚠️
```
Python:     Return: 15.2%, Trades: 38, Win Rate: 55%
TradingView: Return: 12.8%, Trades: 35, Win Rate: 51%

Difference: 2.4% return, 3 trades, 4% win rate
Verdict: ACCEPTABLE - Minor differences likely due to spread modeling
```

### Example 3: Investigate ❌
```
Python:     Return: 25.0%, Trades: 50, Win Rate: 60%
TradingView: Return: 10.0%, Trades: 30, Win Rate: 45%

Difference: 15% return, 20 trades, 15% win rate
Verdict: SIGNIFICANT - Check data sources and execution logic
```

---

## Tips for Accurate Comparison

1. **Use Same Date Range** - Exact start/end dates
2. **Match Commission** - Use 0.0002 (2 pips) in both systems
3. **Same Timeframe** - 1h, 15m, etc.
4. **No Slippage** - Disable in both systems for comparison
5. **Close Open Trades** - Use `finalize_trades=True` in Python

---

## Quick Reference

```bash
# All scripts in one folder
ls tradingview_integration/

# Run all comparisons
cd /Users/levtheswag/ForexBacktesting
source .venv/bin/activate
python tradingview_integration/download_tradingview_data.py
python tradingview_integration/compare_strategies.py
python tradingview_integration/analyze_differences.py

# Check MCP server status
ls ~/TradingViewMCP/tradingview-mcp/
```

---

**Result:** Validate your Python backtests match real-world TradingView results within 1-3%! 🎯
