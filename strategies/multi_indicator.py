"""
Multi-Indicator Strategy

Combines multiple indicators for stronger signals:
- Trend: Moving Average
- Momentum: RSI
- Trend Strength: ADX
- Entry Timing: MACD

Only enters trades when all indicators align.
"""

from strategies.base_strategy import BaseStrategy
import talib


class MultiIndicator(BaseStrategy):
    """
    Multi-Indicator Strategy

    Combines multiple technical indicators for confirmation:
    1. MA: Determines overall trend direction
    2. RSI: Confirms not overbought/oversold
    3. ADX: Confirms trend strength
    4. MACD: Provides entry timing

    Entry Requirements (Long):
    - Price above MA (uptrend)
    - RSI between 40-60 (not extreme)
    - ADX > threshold (strong trend)
    - MACD crosses above signal

    This is more conservative but potentially more accurate.
    """

    # Moving Average (Trend Filter)
    ma_period = 50
    ma_type = 'EMA'  # 'SMA' or 'EMA'

    # RSI (Momentum Filter)
    rsi_period = 14
    rsi_min = 40   # Don't buy if RSI below this (too oversold)
    rsi_max = 60   # Don't buy if RSI above this (too overbought)

    # ADX (Trend Strength Filter)
    adx_period = 14
    adx_threshold = 25  # Minimum ADX to consider trend strong

    # MACD (Entry Timing)
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9

    # Risk Management
    stop_loss_pct = 0.015   # 1.5% stop loss
    take_profit_pct = 0.03  # 3% take profit

    def init(self):
        """Calculate all indicators"""
        # Trend filter
        if self.ma_type == 'EMA':
            self.ma = self.I(talib.EMA, self.data.Close, self.ma_period)
        else:
            self.ma = self.I(talib.SMA, self.data.Close, self.ma_period)

        # Momentum filter
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)

        # Trend strength filter
        self.adx = self.I(
            talib.ADX,
            self.data.High,
            self.data.Low,
            self.data.Close,
            self.adx_period
        )

        # Entry timing
        macd_result = self.I(
            talib.MACD,
            self.data.Close,
            fastperiod=self.macd_fast,
            slowperiod=self.macd_slow,
            signalperiod=self.macd_signal
        )
        self.macd = macd_result[0]
        self.macd_signal_line = macd_result[1]

    def next(self):
        """Execute trading logic with multiple confirmations"""
        price = self.data.Close[-1]

        # Wait for all indicators to be ready
        if len(self.ma) < 2 or len(self.rsi) < 1 or len(self.adx) < 1:
            return

        # Check all conditions for long entry
        if not self.position:
            if self._check_long_conditions(price):
                sl = self.calculate_stop_loss(price, is_long=True)
                tp = self.calculate_take_profit(price, is_long=True)
                self.buy_with_sl_tp(stop_loss=sl, take_profit=tp)

        # Exit conditions
        elif self.position.is_long:
            if self._check_exit_conditions(price):
                self.position.close()

    def _check_long_conditions(self, price):
        """Check if all conditions align for a long entry"""
        # 1. Trend Filter: Price above MA
        uptrend = price > self.ma[-1]
        if not uptrend:
            return False

        # 2. Momentum Filter: RSI in acceptable range
        rsi_ok = self.rsi_min < self.rsi[-1] < self.rsi_max
        if not rsi_ok:
            return False

        # 3. Trend Strength: ADX above threshold
        strong_trend = self.adx[-1] > self.adx_threshold
        if not strong_trend:
            return False

        # 4. Entry Timing: MACD crosses above signal
        macd_cross = self.crossover(self.macd, self.macd_signal_line)
        if not macd_cross:
            return False

        # All conditions met!
        return True

    def _check_exit_conditions(self, price):
        """Check if exit conditions are met"""
        # Exit if price crosses below MA (trend reversal)
        if price < self.ma[-1]:
            return True

        # Exit if MACD crosses below signal (momentum reversal)
        if self.crossunder(self.macd, self.macd_signal_line):
            return True

        # Exit if RSI becomes overbought (>70)
        if self.rsi[-1] > 70:
            return True

        return False