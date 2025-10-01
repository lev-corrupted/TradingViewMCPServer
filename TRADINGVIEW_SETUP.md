# TradingView Integration - Quick Setup Guide

**Connect your Python backtesting system to TradingView for validation**

---

## ✅ What's Already Done

1. ✅ **TradingView MCP Server Installed**
   - Location: `~/TradingViewMCP/tradingview-mcp`
   - Can fetch live TradingView data

2. ✅ **Comparison Scripts Created**
   - `tradingview_integration/download_tradingview_data.py`
   - `tradingview_integration/compare_strategies.py`
   - `tradingview_integration/analyze_differences.py`

3. ✅ **All Scripts Tested & Working**
   - Data comparison: ✅ EURUSD, GBPUSD, USDJPY all < 0.03% difference
   - Strategy backtest: ✅ Generated results (2.87% return on EURUSD)
   - Analysis tool: ✅ Ready to use

4. ✅ **USER_GUIDE.md Simplified**
   - Reduced from 912 lines → 425 lines (53% shorter)
   - Clearer structure, easier to follow

---

## 🔧 What You Need To Do (5 minutes)

### Optional: Enable MCP in Claude Desktop

**Only do this if you want Claude Desktop to access TradingView data directly.**

#### Step 1: Edit Claude Desktop Config

```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### Step 2: Paste This Configuration

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

#### Step 3: Save & Restart

- Save: `Ctrl+X`, then `Y`, then `Enter`
- Quit Claude Desktop: `Cmd+Q`
- Reopen Claude Desktop
- Look for 🔌 icon (bottom right)

#### Step 4: Test It

In Claude Desktop, try:
```
Show me the top 10 most volatile forex pairs right now
```

---

## 🚀 How To Use (3 commands)

### 1. Compare Data Sources

```bash
source .venv/bin/activate
python tradingview_integration/download_tradingview_data.py
```

**What you'll see:**
- TradingView current prices vs yfinance
- Should be < 0.1% difference (means data is accurate)

### 2. Run Python Backtest

```bash
python tradingview_integration/compare_strategies.py
```

**What you'll get:**
- Python backtest results
- Exact parameters to use in TradingView
- CSV file with results

### 3. Compare Results

After running the same strategy in TradingView:

```bash
python tradingview_integration/analyze_differences.py
```

**Enter your results and get analysis:**
- < 2% difference = EXCELLENT
- < 5% difference = ACCEPTABLE
- \> 5% difference = Investigate

---

## 📊 Example Workflow

### Your Python Strategy

```python
# Test your strategy in Python
from backtester import quick_backtest
from strategies.ma_crossover import MACrossover

quick_backtest(MACrossover, pair='EURUSD', timeframe='1h')
```

### Convert to Pine Script

**In Claude Desktop (with MCP enabled), ask:**
```
Convert this Python strategy to Pine Script v5:
- 10-period fast MA
- 20-period slow MA
- Buy when fast crosses above slow
- Sell when fast crosses below slow
```

### Test in TradingView

1. Paste Pine Script into TradingView
2. Run backtest on same dates
3. Compare results

### Validate Accuracy

```bash
python tradingview_integration/analyze_differences.py
```

---

## 📁 Directory Structure

```
ForexBacktesting/
├── strategy_manager.py          # Main interface
├── backtester.py                # Core engine
├── forex_config.py              # Spread configuration
├── USER_GUIDE.md               # Simplified guide
│
├── strategies/                  # Your strategies
├── data/                       # Market data
├── tests/                      # Test scripts
├── examples/                   # Demo scripts
├── reports/                    # HTML reports
│
└── tradingview_integration/    # NEW: TradingView tools
    ├── README.md              # Detailed guide
    ├── download_tradingview_data.py
    ├── compare_strategies.py
    └── analyze_differences.py
```

---

## 🎯 Quick Reference

```bash
# Activate environment (always do this first)
source .venv/bin/activate

# Test TradingView data accuracy
python tradingview_integration/download_tradingview_data.py

# Run Python backtest for comparison
python tradingview_integration/compare_strategies.py

# Compare with TradingView results
python tradingview_integration/analyze_differences.py

# Run your main system
python strategy_manager.py
```

---

## 🔍 Test Results

All scripts tested and working:

**1. Data Comparison (download_tradingview_data.py)**
```
EURUSD: 0.029% difference ✅
GBPUSD: 0.007% difference ✅
USDJPY: 0.004% difference ✅
```

**2. Strategy Backtest (compare_strategies.py)**
```
EURUSD MA Crossover (2023-01-01 to 2024-09-01):
Return: 2.87%
Sharpe Ratio: 0.37
Max Drawdown: -3.84%
Win Rate: 37.5%
Total Trades: 8
```

**3. Analysis Tool (analyze_differences.py)**
```
Interactive comparison ready to use ✅
```

---

## ❓ Need Help?

**For system help:**
- Read [USER_GUIDE.md](USER_GUIDE.md) (now simplified!)

**For TradingView integration:**
- Read [tradingview_integration/README.md](tradingview_integration/README.md)

**Run tests:**
```bash
python tests/test_system.py
```

---

## 📝 Note on PineScript MCP

The `pinescript-mcp-server` package doesn't exist on npm yet. The guide you provided had incorrect installation instructions. The TradingView Data MCP server is installed and working, which gives you:

✅ Real-time market data from TradingView
✅ Technical indicators
✅ Top gainers/losers
✅ RSI, MACD, Bollinger Bands data

For Pine Script code generation, you can still use Claude Desktop without MCP - just describe your strategy and ask for Pine Script code.

---

**Ready to validate your backtests! 🎯**
