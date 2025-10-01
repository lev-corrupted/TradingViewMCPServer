#!/usr/bin/env python3
"""
Your First Forex Backtest
EUR/USD Moving Average Crossover Strategy
"""

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import yfinance as yf

class ForexMAStrategy(Strategy):
    # Parameters you can optimize later
    fast_period = 10
    slow_period = 30
    
    def init(self):
        # Calculate moving averages
        close = pd.Series(self.data.Close)
        self.fast_ma = self.I(lambda x: pd.Series(x).rolling(self.fast_period).mean(), self.data.Close)
        self.slow_ma = self.I(lambda x: pd.Series(x).rolling(self.slow_period).mean(), self.data.Close)
    
    def next(self):
        # Buy when fast MA crosses above slow MA
        if crossover(self.fast_ma, self.slow_ma):
            if not self.position:
                self.buy()
        
        # Sell when fast MA crosses below slow MA
        elif crossover(self.slow_ma, self.fast_ma):
            if self.position:
                self.position.close()

# Download EUR/USD data
print("Downloading EUR/USD data...")
data = yf.download("EURUSD=X", start="2023-01-01", end="2024-09-01", progress=False)
data = data[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()

print(f"Downloaded {len(data)} days of data")

# Run backtest
print("\nRunning backtest...")
bt = Backtest(
    data, 
    ForexMAStrategy,
    cash=10000,
    commission=0.0002,  # 2 pip spread
    exclusive_orders=True
)

# Run the backtest
results = bt.run()

# Display results
print("\n=== BACKTEST RESULTS ===")
print(f"Return: {results['Return [%]']:.2f}%")
print(f"Sharpe Ratio: {results.get('Sharpe Ratio', 0):.2f}")
print(f"Max Drawdown: {results['Max. Drawdown [%]']:.2f}%")
print(f"Total Trades: {results['# Trades']}")
print(f"Win Rate: {results.get('Win Rate [%]', 0):.1f}%")

# Open interactive chart
print("\nOpening interactive chart in your browser...")
bt.plot()

print("\n✅ Backtest complete! Check the chart in your browser.")
