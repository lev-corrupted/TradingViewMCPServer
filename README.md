# BackTestTradingViewMCP

**Complete forex backtesting system with TradingView integration for validation and real-time market data**

---

## What This Is

A unified system that combines:

1. **Forex Backtesting Engine** - Test trading strategies with realistic spreads and multi-timeframe support
2. **TradingView MCP Server** - Real-time market data and technical indicators
3. **Validation Tools** - Compare Python backtests with TradingView results

---

## Quick Start (3 Steps)

```bash
# 1. Install dependencies
cd ~/BackTestTradingViewMCP
uv sync

# 2. Activate environment
source .venv/bin/activate

# 3. Run interactive strategy manager
python strategy_manager.py
```

---

## Key Features

### Backtesting System ✨

- **Realistic Spreads**: 1-150 pips based on pair and timeframe
- **Multi-Timeframe**: Test on 5m, 15m, 30m, 1h, 4h, 1d charts
- **5 Example Strategies**: MA Crossover, RSI, MACD, Bollinger Bands, Multi-Indicator
- **Auto-Discovery**: Drop strategies in `strategies/` folder - they auto-appear
- **Interactive CLI**: Beautiful terminal interface with Rich
- **Smart Caching**: Downloaded data cached locally

### TradingView Integration 🔗

- **Real-Time Data**: Live prices, volume, technical indicators
- **Market Screener**: Top gainers, losers, volatile pairs
- **Validation Tools**: Compare backtest results with TradingView
- **MCP Server**: Connect Claude Desktop to TradingView data

### Validation & Comparison 🎯

- **Data Accuracy Check**: Verify yfinance vs TradingView prices
- **Strategy Comparison**: Backtest same strategy in both systems
- **Difference Analyzer**: Identify discrepancies in results

---

## Project Structure

```
BackTestTradingViewMCP/
├── strategy_manager.py          # Main interface - START HERE
├── backtester.py                # Backtesting engine
├── forex_config.py              # Spread/leverage configuration
│
├── strategies/                  # Trading strategies
│   ├── ma_crossover.py
│   ├── rsi_strategy.py
│   ├── macd_strategy.py
│   ├── bollinger_strategy.py
│   ├── multi_indicator.py
│   └── template.py              # Copy this to create new strategies
│
├── mcp_server/                  # TradingView MCP server
│   └── tradingview_mcp/
│       ├── server.py            # MCP server entry point
│       └── coinlist/            # Supported assets
│
├── tradingview_integration/     # Validation tools
│   ├── download_tradingview_data.py   # Data comparison
│   ├── compare_strategies.py          # Backtest comparison
│   └── analyze_differences.py         # Results analyzer
│
├── data/                        # Market data cache
├── tests/                       # Test scripts
├── examples/                    # Demo scripts
└── utils/                       # Helper modules
```

---

## Installation

### Prerequisites

- macOS / Linux / Windows
- Python 3.13+
- UV package manager

### Setup

```bash
# Navigate to project
cd ~/BackTestTradingViewMCP

# Install all dependencies (backtesting + MCP server)
uv sync

# Activate environment
source .venv/bin/activate

# Verify installation
python tests/test_system.py
```

---

## Usage

### 1. Backtesting

```bash
# Interactive menu (easiest)
python strategy_manager.py

# Quick test
python examples/quickstart.py
```

### 2. TradingView Validation

```bash
# Check data accuracy
python tradingview_integration/download_tradingview_data.py

# Run backtest for comparison
python tradingview_integration/compare_strategies.py

# Compare results
python tradingview_integration/analyze_differences.py
```

### 3. MCP Server (for Claude Desktop)

1. Edit config:
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

2. Add:
```json
{
  "mcpServers": {
    "tradingview-data": {
      "command": "uv",
      "args": ["run", "python", "mcp_server/tradingview_mcp/server.py"],
      "cwd": "/Users/levtheswag/BackTestTradingViewMCP"
    }
  }
}
```

3. Restart Claude Desktop (Cmd+Q, reopen)

---

## Creating Strategies

```bash
# Copy template
cp strategies/template.py strategies/my_strategy.py

# Edit and test
python strategy_manager.py
```

---

## Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete usage guide
- **[TRADINGVIEW_SETUP.md](TRADINGVIEW_SETUP.md)** - Integration setup
- **[tradingview_integration/README.md](tradingview_integration/README.md)** - Validation tools
- **[PROJECT_NOTES.md](PROJECT_NOTES.md)** - Technical details

---

## Testing

```bash
# Run all tests
python tests/test_system.py

# Test data comparison
python tradingview_integration/download_tradingview_data.py
```

---

## What Makes This Different

1. **Realistic Spreads** - 1-150 pips based on actual market conditions
2. **TradingView Validation** - Compare backtests (should match within 1-3%)
3. **Live Market Data** - Real-time TradingView data via MCP
4. **Multi-Timeframe** - 5m to 1d with automatic spread adjustment
5. **Auto-Discovery** - Drop strategies in folder, auto-appear in menus

---

**Happy Trading! 📈**

*Backtest with confidence. Validate with precision.*
