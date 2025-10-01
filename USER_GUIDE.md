# Forex Backtesting System - User Guide

**Test forex trading strategies with realistic spreads and multiple timeframes**

---

## Quick Start (3 Steps)

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Run interactive menu
python strategy_manager.py

# 3. Choose a strategy and pair - that's it!
```

---

## What's New ✨

**Realistic Spreads** - Automatic spread calculation (1-150 pips based on pair)
**Multi-Timeframe** - Test on 5m, 15m, 30m, 1h, 4h, 1d charts
**Auto-Leverage** - Realistic leverage per pair type (majors/crosses/exotics)

---

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Creating Strategies](#creating-strategies)
3. [Testing & Results](#testing--results)
4. [Available Indicators](#available-indicators)
5. [Examples](#examples)
6. [Troubleshooting](#troubleshooting)

---

## Basic Usage

### Interactive Menu (Easiest)

```bash
python strategy_manager.py
```

**Options:**
1. Run Single Strategy
2. Compare Strategies
3. Test on Multiple Pairs
4. Optimize Strategy
5. List Strategies
6. Download Data

### Python Code

```python
from backtester import quick_backtest
from strategies.ma_crossover import MACrossover

# Simple test
quick_backtest(MACrossover, pair='EURUSD', show_plot=True)

# With timeframe
quick_backtest(MACrossover, pair='EURUSD', timeframe='15m')
```

### Advanced Python

```python
from backtester import ForexBacktester
from strategies.ma_crossover import MACrossover

backtester = ForexBacktester()

# Single backtest
results = backtester.run(
    strategy=MACrossover,
    pair='EURUSD',
    timeframe='1h',
    start='2024-01-01'
)

# Compare strategies
results = backtester.run_multiple(
    strategies={'MA': MACrossover, 'RSI': RSIStrategy},
    pair='EURUSD',
    timeframe='15m'
)

# Test multiple pairs
results = backtester.run_on_multiple_pairs(
    strategy=MACrossover,
    pairs=['EURUSD', 'GBPUSD', 'USDJPY'],
    timeframe='1h'
)
```

---

## Creating Strategies

### Step 1: Copy Template

```bash
cp strategies/template.py strategies/my_strategy.py
```

### Step 2: Edit File

```python
from strategies.base_strategy import BaseStrategy
import talib

class MyStrategy(BaseStrategy):
    """Simple RSI Strategy"""

    # Parameters
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70
    stop_loss_pct = 0.02

    def init(self):
        """Calculate indicators (called once)"""
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)

    def next(self):
        """Trading logic (called every bar)"""
        price = self.data.Close[-1]

        # Buy when oversold
        if self.rsi[-1] < self.rsi_oversold and not self.position:
            sl = self.calculate_stop_loss(price, is_long=True)
            self.buy_with_sl_tp(stop_loss=sl)

        # Sell when overbought
        elif self.rsi[-1] > self.rsi_overbought and self.position:
            self.position.close()
```

### Step 3: Test It

```bash
python strategy_manager.py
# Your strategy will auto-appear in the menu!
```

---

## Key Concepts

### Trading Methods

```python
self.buy()                    # Open long position
self.sell()                   # Open short position
self.position.close()         # Close position
self.buy_with_sl_tp(sl, tp)  # Buy with stop/target
```

### Data Access

```python
self.data.Close[-1]          # Current close price
self.data.Close[-2]          # Previous close price
self.position                # Current position
self.position.is_long        # True if long
```

### Helper Methods

```python
self.crossover(a, b)         # A crosses above B
self.crossunder(a, b)        # A crosses below B
self.calculate_stop_loss()   # Calculate SL price
```

---

## Available Indicators

### Trend

```python
# Moving Averages
self.sma = self.I(talib.SMA, self.data.Close, 20)
self.ema = self.I(talib.EMA, self.data.Close, 20)

# MACD
macd, signal, hist = self.I(talib.MACD, self.data.Close)
```

### Momentum

```python
# RSI
self.rsi = self.I(talib.RSI, self.data.Close, 14)

# Stochastic
slowk, slowd = self.I(talib.STOCH, self.data.High, self.data.Low, self.data.Close)
```

### Volatility

```python
# Bollinger Bands
upper, middle, lower = self.I(talib.BBANDS, self.data.Close, 20)

# ATR
self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14)
```

### Trend Strength

```python
# ADX
self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, 14)
```

---

## Testing & Results

### Understanding Results

**Good Strategy:**
- Total Return > 0%
- Sharpe Ratio > 1.0
- Max Drawdown < 20%
- Win Rate > 50%
- Profit Factor > 1.5

**Key Metrics:**
- **Return %** - Total profit/loss
- **Sharpe Ratio** - Risk-adjusted return (higher = better)
- **Max Drawdown %** - Worst loss from peak
- **Win Rate %** - Winning trades percentage
- **Profit Factor** - Total wins ÷ Total losses

### Realistic Spreads

The system automatically calculates spreads:

| Pair | 1h Spread | 15m Spread | 5m Spread |
|------|-----------|------------|-----------|
| EURUSD | 1.1 pips | 1.3 pips | 1.5 pips |
| GBPJPY | 2.5 pips | 3.2 pips | 3.7 pips |
| USDTRY | 110 pips | 130 pips | 150 pips |

**Lower timeframes = wider spreads** (more trading frequency = higher costs)

### Timeframes

- **5m, 15m, 30m** - Scalping/intraday (60 days max data)
- **1h, 4h** - Swing trading
- **1d** - Position trading

---

## Examples

### Example 1: MA Crossover

```python
class MACrossover(BaseStrategy):
    fast_period = 10
    slow_period = 30

    def init(self):
        self.fast_ma = self.I(talib.SMA, self.data.Close, self.fast_period)
        self.slow_ma = self.I(talib.SMA, self.data.Close, self.slow_period)

    def next(self):
        if self.crossover(self.fast_ma, self.slow_ma):
            if not self.position:
                self.buy()
        elif self.crossunder(self.fast_ma, self.slow_ma):
            if self.position:
                self.position.close()
```

### Example 2: RSI Strategy

```python
class RSIStrategy(BaseStrategy):
    rsi_period = 14
    oversold = 30
    overbought = 70

    def init(self):
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)

    def next(self):
        if self.rsi[-1] < self.oversold and not self.position:
            self.buy()
        elif self.rsi[-1] > self.overbought and self.position:
            self.position.close()
```

### Example 3: Bollinger Bands

```python
class BollingerStrategy(BaseStrategy):
    bb_period = 20
    bb_std = 2

    def init(self):
        upper, middle, lower = self.I(talib.BBANDS, self.data.Close, self.bb_period)
        self.bb_upper = upper
        self.bb_middle = middle
        self.bb_lower = lower

    def next(self):
        price = self.data.Close[-1]

        # Buy at lower band
        if price <= self.bb_lower[-1] and not self.position:
            self.buy()

        # Sell at upper band
        elif price >= self.bb_upper[-1] and self.position:
            self.position.close()
```

---

## Troubleshooting

### Strategy Not Showing

- File must be in `strategies/` folder
- Must inherit from `BaseStrategy`
- Check for syntax errors
- Restart `strategy_manager.py`

### No Trades

- Increase date range
- Check indicator needs enough bars
- Try different pairs/timeframes
- Add debug prints in `next()`

### Indicator Errors

```python
def next(self):
    # Always check enough data exists
    if len(self.rsi) < 2:
        return

    # Now safe to use
    if self.rsi[-1] < 30:
        self.buy()
```

### Data Download Issues

- Check internet connection
- Verify pair name (EURUSD not EUR/USD)
- Some exotic pairs have limited data
- Retry if Yahoo Finance times out

---

## Best Practices

1. **Start Simple** - Basic logic first, add complexity later
2. **Test Thoroughly** - Use 6+ months of data
3. **Multiple Pairs** - Good strategies work across markets
4. **Use Stop Losses** - Always protect capital
5. **Be Realistic** - Backtests ≠ real trading
6. **Paper Trade First** - Test before risking money

---

## Supported Pairs

**Majors (Tight Spreads):**
EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD

**Crosses (Higher Volatility):**
GBPJPY, EURJPY, AUDJPY, EURGBP, EURAUD

**Exotics (Very Volatile):**
USDTRY, USDZAR, USDMXN, USDBRL

---

## Quick Reference

```bash
# Activate environment
source .venv/bin/activate

# Interactive mode
python strategy_manager.py

# Run tests
python tests/test_system.py

# Quick demo
python examples/quickstart.py

# Create strategy
cp strategies/template.py strategies/my_strategy.py
```

---

## Need Help?

1. Check example strategies in `strategies/` folder
2. Run `python tests/test_system.py` to verify setup
3. Review troubleshooting section above

---

**Remember:** This is for educational purposes. Past performance ≠ future results. Always use proper risk management.

---

**Happy Trading! 📈**
