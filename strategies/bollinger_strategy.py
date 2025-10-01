"""
Bollinger Bands Strategy

Trades based on Bollinger Bands breakouts and mean reversion:
- Mean Reversion: Buy at lower band, sell at upper band
- Breakout: Buy when price breaks above upper band (momentum)

Can be configured for either mean reversion or breakout mode.
"""

from strategies.base_strategy import BaseStrategy
import talib


class BollingerStrategy(BaseStrategy):
    """
    Bollinger Bands Strategy

    Bollinger Bands consist of:
    - Middle Band: Simple moving average
    - Upper Band: Middle + (2 * standard deviation)
    - Lower Band: Middle - (2 * standard deviation)

    Two trading modes:
    1. Mean Reversion: Buy at lower band, sell at upper band
    2. Breakout: Buy when price breaks above upper band
    """

    # Bollinger Bands parameters
    bb_period = 20        # Moving average period
    bb_std = 2            # Number of standard deviations

    # Strategy mode
    mode = 'mean_reversion'  # 'mean_reversion' or 'breakout'

    # Mean reversion settings
    exit_at_middle = True    # Exit position when price reaches middle band

    # Risk management
    stop_loss_pct = 0.02

    def init(self):
        """Calculate Bollinger Bands"""
        bb_result = self.I(
            talib.BBANDS,
            self.data.Close,
            timeperiod=self.bb_period,
            nbdevup=self.bb_std,
            nbdevdn=self.bb_std
        )
        self.bb_upper = bb_result[0]
        self.bb_middle = bb_result[1]
        self.bb_lower = bb_result[2]

    def next(self):
        """Execute trading logic"""
        price = self.data.Close[-1]

        if self.mode == 'mean_reversion':
            self._mean_reversion_logic(price)
        elif self.mode == 'breakout':
            self._breakout_logic(price)

    def _mean_reversion_logic(self, price):
        """Mean reversion strategy: Buy at lower band, sell at upper band"""
        # Buy signal: Price touches lower band
        if price <= self.bb_lower[-1] and not self.position:
            sl = self.calculate_stop_loss(price, is_long=True)
            self.buy_with_sl_tp(stop_loss=sl, take_profit=self.bb_upper[-1])

        # Sell signal: Price reaches upper band OR middle band
        elif self.position.is_long:
            if price >= self.bb_upper[-1]:
                self.position.close()
            elif self.exit_at_middle and price >= self.bb_middle[-1]:
                self.position.close()

    def _breakout_logic(self, price):
        """Breakout strategy: Buy when price breaks above upper band"""
        prev_price = self.data.Close[-2]

        # Buy signal: Price breaks above upper band
        if prev_price <= self.bb_upper[-2] and price > self.bb_upper[-1]:
            if not self.position:
                sl = self.calculate_stop_loss(price, is_long=True)
                self.buy_with_sl_tp(stop_loss=sl)

        # Sell signal: Price crosses below middle band
        elif self.position.is_long and price < self.bb_middle[-1]:
            self.position.close()