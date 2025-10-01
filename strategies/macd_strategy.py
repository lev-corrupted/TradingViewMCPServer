"""
MACD Crossover Strategy

Trades based on MACD line and signal line crossovers:
- Buy when MACD line crosses above signal line (bullish momentum)
- Sell when MACD line crosses below signal line (bearish momentum)

MACD is a trend-following momentum indicator.
"""

from strategies.base_strategy import BaseStrategy
import talib


class MACDStrategy(BaseStrategy):
    """
    MACD Crossover Strategy

    Uses MACD (Moving Average Convergence Divergence) to identify momentum:
    - MACD Line: Difference between fast and slow EMA
    - Signal Line: EMA of MACD line
    - Histogram: Difference between MACD and Signal

    Entry: MACD crosses above Signal (bullish momentum)
    Exit: MACD crosses below Signal (bearish momentum)
    """

    # MACD parameters
    fast_period = 12      # Fast EMA period
    slow_period = 26      # Slow EMA period
    signal_period = 9     # Signal line EMA period

    # Optional: Add zero-line filter
    use_zero_filter = False  # Only buy above 0, sell below 0

    # Optional: Add histogram confirmation
    use_histogram = False    # Require histogram to confirm direction

    def init(self):
        """Calculate MACD indicator"""
        macd_result = self.I(
            talib.MACD,
            self.data.Close,
            fastperiod=self.fast_period,
            slowperiod=self.slow_period,
            signalperiod=self.signal_period
        )
        self.macd = macd_result[0]
        self.signal = macd_result[1]
        self.histogram = macd_result[2]

    def next(self):
        """Execute trading logic"""
        # Wait for indicators to be calculated
        if len(self.macd) < 2:
            return

        macd_now = self.macd[-1]
        macd_prev = self.macd[-2]
        signal_now = self.signal[-1]
        signal_prev = self.signal[-2]

        # Buy signal: MACD crosses above Signal
        if macd_prev <= signal_prev and macd_now > signal_now:
            # Optional filters
            if self.use_zero_filter and macd_now < 0:
                return
            if self.use_histogram and self.histogram[-1] < 0:
                return

            if not self.position:
                self.buy()
            elif self.position.is_short:
                self.position.close()
                self.buy()

        # Sell signal: MACD crosses below Signal
        elif macd_prev >= signal_prev and macd_now < signal_now:
            # Optional filters
            if self.use_zero_filter and macd_now > 0:
                return
            if self.use_histogram and self.histogram[-1] > 0:
                return

            if self.position.is_long:
                self.position.close()