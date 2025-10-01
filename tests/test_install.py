#!/usr/bin/env python3
"""Verify forex backtesting setup"""

print("=== FOREX BACKTESTING VERIFICATION ===\n")

# Test 1: Check core packages
packages = ['pandas', 'numpy', 'backtesting', 'yfinance', 'talib', 'bokeh']
for pkg in packages:
    try:
        __import__(pkg)
        print(f"✅ {pkg}")
    except ImportError as e:
        print(f"❌ {pkg} - FAILED: {e}")

# Test 2: Run a simple backtest
print("\n=== RUNNING TEST BACKTEST ===")
try:
    from backtesting import Backtest, Strategy
    from backtesting.test import EURUSD
    from backtesting.lib import crossover
    import pandas as pd
    
    # Simple moving average crossover
    class TestStrategy(Strategy):
        def init(self):
            close = pd.Series(self.data.Close)
            self.sma1 = self.I(lambda x: pd.Series(x).rolling(10).mean(), self.data.Close)
            self.sma2 = self.I(lambda x: pd.Series(x).rolling(20).mean(), self.data.Close)
        
        def next(self):
            if crossover(self.sma1, self.sma2):
                self.buy()
            elif crossover(self.sma2, self.sma1):
                self.sell()
    
    bt = Backtest(EURUSD, TestStrategy, cash=10000, commission=.0002)
    stats = bt.run()
    
    print(f"✅ Backtest completed!")
    print(f"   Return: {stats['Return [%]']:.2f}%")
    print(f"   Trades: {stats['# Trades']}")
    print(f"   Win Rate: {stats.get('Win Rate [%]', 0):.1f}%")
    
    print("\n🎉 ALL SYSTEMS GO - READY FOR FOREX BACKTESTING!")
    
except Exception as e:
    print(f"❌ Backtest failed: {e}")
    import traceback
    traceback.print_exc()

