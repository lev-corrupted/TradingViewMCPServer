#!/usr/bin/env python3
"""
Compare your Python backtest results with TradingView results
"""

import pandas as pd
import yfinance as yf
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class MAStrategy(Strategy):
    """Simple MA Crossover - matches TradingView strategy"""
    fast = 10
    slow = 20

    def init(self):
        close = pd.Series(self.data.Close)
        self.ma_fast = self.I(lambda x: pd.Series(x).rolling(self.fast).mean(), self.data.Close)
        self.ma_slow = self.I(lambda x: pd.Series(x).rolling(self.slow).mean(), self.data.Close)

    def next(self):
        if crossover(self.ma_fast, self.ma_slow):
            if not self.position:
                self.buy()
        elif crossover(self.ma_slow, self.ma_fast):
            if self.position:
                self.position.close()

def backtest_and_save_results(symbol="EURUSD", start="2023-01-01", end="2024-09-01"):
    """Run backtest and save results to compare with TradingView"""

    print("="*70)
    print(f"BACKTESTING: {symbol}")
    print("="*70)

    # Download data
    print("\n1. Downloading data...")
    data = yf.download(f"{symbol}=X", start=start, end=end, progress=False)

    # Fix MultiIndex columns if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    data = data[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    print(f"   ✅ Downloaded {len(data)} bars")

    # Run backtest
    print("\n2. Running backtest...")
    bt = Backtest(data, MAStrategy, cash=10000, commission=0.0002)
    results = bt.run()

    # Display results
    print("\n" + "="*70)
    print("PYTHON BACKTEST RESULTS")
    print("="*70)
    print(f"Return: {results['Return [%]']:.2f}%")
    print(f"Sharpe Ratio: {results.get('Sharpe Ratio', 0):.2f}")
    print(f"Max Drawdown: {results['Max. Drawdown [%]']:.2f}%")
    print(f"Win Rate: {results.get('Win Rate [%]', 0):.1f}%")
    print(f"Total Trades: {results['# Trades']}")
    print(f"Avg Trade: {results.get('Avg. Trade [%]', 0):.2f}%")

    # Save results
    results_dict = {
        'Symbol': symbol,
        'Start Date': start,
        'End Date': end,
        'Return %': results['Return [%]'],
        'Sharpe Ratio': results.get('Sharpe Ratio', 0),
        'Max Drawdown %': results['Max. Drawdown [%]'],
        'Win Rate %': results.get('Win Rate [%]', 0),
        'Total Trades': results['# Trades'],
    }

    df = pd.DataFrame([results_dict])
    df.to_csv(f'backtest_results_{symbol}.csv', index=False)
    print(f"\n✅ Results saved to: backtest_results_{symbol}.csv")

    print("\n" + "="*70)
    print("NEXT STEPS TO COMPARE WITH TRADINGVIEW:")
    print("="*70)
    print("1. Open TradingView and create the same strategy")
    print("2. Use these exact parameters:")
    print(f"   - Fast MA: {results._strategy.fast}")
    print(f"   - Slow MA: {results._strategy.slow}")
    print(f"   - Period: {start} to {end}")
    print("3. Run TradingView backtest")
    print("4. Compare the results!")
    print("\nExpected TradingView results should be within 1-2% of these values")

    return results

if __name__ == "__main__":
    # Test on EUR/USD
    backtest_and_save_results("EURUSD")
