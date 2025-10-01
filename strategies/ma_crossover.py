"""
Moving Average Crossover Strategy

Classic trend-following strategy:
- Buy when fast MA crosses above slow MA (golden cross)
- Sell when fast MA crosses below slow MA (death cross)

Works best in trending markets. Performs poorly in ranging markets.
"""

from strategies.base_strategy import BaseStrategy
import talib


class MACrossover(BaseStrategy):
    """
    Moving Average Crossover Strategy

    Uses two moving averages to identify trend changes:
    - Fast MA (shorter period) responds quickly to price changes
    - Slow MA (longer period) filters out noise

    Entry: Fast MA crosses above Slow MA (bullish)
    Exit: Fast MA crosses below Slow MA (bearish)
    """

    # Strategy parameters (can be optimized)
    fast_period = 10  # Fast moving average period
    slow_period = 30  # Slow moving average period
    ma_type = 'SMA'   # Type: 'SMA' or 'EMA'

    # Risk management (optional)
    # stop_loss_pct = 0.02
    # take_profit_pct = 0.04

    def init(self):
        """Calculate moving averages"""
        if self.ma_type == 'EMA':
            self.fast_ma = self.I(talib.EMA, self.data.Close, self.fast_period)
            self.slow_ma = self.I(talib.EMA, self.data.Close, self.slow_period)
        else:  # SMA (default)
            self.fast_ma = self.I(talib.SMA, self.data.Close, self.fast_period)
            self.slow_ma = self.I(talib.SMA, self.data.Close, self.slow_period)

    def next(self):
        """Execute trading logic"""
        # Buy signal: Fast MA crosses above Slow MA
        if self.crossover(self.fast_ma, self.slow_ma):
            if not self.position:
                self.buy()
            elif self.position.is_short:
                self.position.close()
                self.buy()

        # Sell signal: Fast MA crosses below Slow MA
        elif self.crossunder(self.fast_ma, self.slow_ma):
            if self.position.is_long:
                self.position.close()