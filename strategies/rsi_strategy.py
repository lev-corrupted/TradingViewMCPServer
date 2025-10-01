"""
RSI Mean Reversion Strategy

Trades based on RSI overbought/oversold levels:
- Buy when RSI crosses below oversold threshold (expecting bounce)
- Sell when RSI crosses above overbought threshold (expecting pullback)

Works best in ranging markets. Can give false signals in strong trends.
"""

from strategies.base_strategy import BaseStrategy
import talib


class RSIStrategy(BaseStrategy):
    """
    RSI Mean Reversion Strategy

    Uses Relative Strength Index (RSI) to identify overbought/oversold conditions:
    - RSI < 30: Oversold (potential buy)
    - RSI > 70: Overbought (potential sell)

    Entry: RSI crosses below oversold level
    Exit: RSI crosses above overbought level OR price reaches target
    """

    # Strategy parameters
    rsi_period = 14         # RSI calculation period
    rsi_oversold = 30       # Oversold threshold (buy signal)
    rsi_overbought = 70     # Overbought threshold (sell signal)

    # Optional: Add trend filter
    use_trend_filter = False  # Only trade in direction of trend
    trend_ma_period = 200     # MA period for trend filter

    # Risk management
    stop_loss_pct = 0.02      # 2% stop loss
    take_profit_pct = 0.04    # 4% take profit

    def init(self):
        """Calculate RSI and optional trend filter"""
        # RSI indicator
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)

        # Optional trend filter
        if self.use_trend_filter:
            self.trend_ma = self.I(talib.SMA, self.data.Close, self.trend_ma_period)

    def next(self):
        """Execute trading logic"""
        price = self.data.Close[-1]

        # Check trend direction if filter is enabled
        uptrend = True
        downtrend = True
        if self.use_trend_filter:
            uptrend = price > self.trend_ma[-1]
            downtrend = price < self.trend_ma[-1]

        # Buy signal: RSI oversold
        if self.rsi[-1] < self.rsi_oversold and not self.position and uptrend:
            sl = self.calculate_stop_loss(price, is_long=True)
            tp = self.calculate_take_profit(price, is_long=True)
            self.buy_with_sl_tp(stop_loss=sl, take_profit=tp)

        # Sell signal: RSI overbought
        elif self.rsi[-1] > self.rsi_overbought and self.position.is_long:
            self.position.close()

        # Exit on opposite signal
        elif self.rsi[-1] > self.rsi_overbought and not self.position and downtrend:
            # Optional: Enable short selling
            # sl = self.calculate_stop_loss(price, is_long=False)
            # tp = self.calculate_take_profit(price, is_long=False)
            # self.sell_with_sl_tp(stop_loss=sl, take_profit=tp)
            pass