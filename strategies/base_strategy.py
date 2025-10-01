"""
Base Strategy Class for Forex Backtesting

All trading strategies should inherit from BaseStrategy to ensure
consistency and access to common functionality.
"""

from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import talib
from typing import Optional


class BaseStrategy(Strategy):
    """
    Base class for all forex trading strategies.

    Provides common functionality and standardized interface:
    - Automatic indicator calculation helpers
    - Position sizing utilities
    - Risk management defaults
    - Consistent parameter handling

    To create a new strategy:
    1. Inherit from this class
    2. Define parameters as class variables
    3. Override init() to calculate indicators
    4. Override next() with your trading logic

    Example:
    --------
    class MyStrategy(BaseStrategy):
        # Parameters
        period = 20

        def init(self):
            self.sma = self.I(talib.SMA, self.data.Close, self.period)

        def next(self):
            if self.data.Close[-1] > self.sma[-1]:
                self.buy()
            elif self.data.Close[-1] < self.sma[-1]:
                self.sell()
    """

    # Default risk management parameters
    # Override these in your strategy class if needed
    stop_loss_pct: Optional[float] = None  # Stop loss as % of entry price (e.g., 0.02 = 2%)
    take_profit_pct: Optional[float] = None  # Take profit as % of entry price
    position_size: float = 1.0  # Fraction of equity to risk per trade (0.0 to 1.0)

    def init(self):
        """
        Initialize indicators and strategy state.

        Override this method in your strategy to:
        - Calculate technical indicators
        - Set up any variables needed for trading logic

        Example:
        --------
        def init(self):
            self.sma = self.I(talib.SMA, self.data.Close, 20)
            self.rsi = self.I(talib.RSI, self.data.Close, 14)
        """
        pass

    def next(self):
        """
        Execute trading logic for the current bar.

        Override this method with your strategy's logic:
        - Check conditions for entry/exit
        - Place buy/sell orders
        - Manage positions

        Example:
        --------
        def next(self):
            if self.rsi[-1] < 30 and not self.position:
                self.buy()
            elif self.rsi[-1] > 70 and self.position:
                self.position.close()
        """
        pass

    # ===== HELPER METHODS =====
    # These methods are available to all strategies

    def buy_with_sl_tp(self,
                       stop_loss: Optional[float] = None,
                       take_profit: Optional[float] = None,
                       size: Optional[float] = None):
        """
        Buy with automatic stop loss and take profit.

        Parameters:
        -----------
        stop_loss : float, optional
            Stop loss price (absolute price, not percentage)
        take_profit : float, optional
            Take profit price (absolute price, not percentage)
        size : float, optional
            Position size (fraction of equity)

        Example:
        --------
        # Buy with 2% stop loss and 4% take profit
        current_price = self.data.Close[-1]
        self.buy_with_sl_tp(
            stop_loss=current_price * 0.98,
            take_profit=current_price * 1.04
        )
        """
        if size is None:
            size = self.position_size

        self.buy(sl=stop_loss, tp=take_profit, size=size)

    def sell_with_sl_tp(self,
                        stop_loss: Optional[float] = None,
                        take_profit: Optional[float] = None,
                        size: Optional[float] = None):
        """
        Sell with automatic stop loss and take profit.

        Parameters:
        -----------
        stop_loss : float, optional
            Stop loss price (absolute price, not percentage)
        take_profit : float, optional
            Take profit price (absolute price, not percentage)
        size : float, optional
            Position size (fraction of equity)
        """
        if size is None:
            size = self.position_size

        self.sell(sl=stop_loss, tp=take_profit, size=size)

    def calculate_stop_loss(self, entry_price: float, is_long: bool = True) -> Optional[float]:
        """
        Calculate stop loss price based on strategy's stop_loss_pct.

        Parameters:
        -----------
        entry_price : float
            Entry price for the position
        is_long : bool
            True for long positions, False for short positions

        Returns:
        --------
        float or None
            Stop loss price, or None if stop_loss_pct not set
        """
        if self.stop_loss_pct is None:
            return None

        if is_long:
            return entry_price * (1 - self.stop_loss_pct)
        else:
            return entry_price * (1 + self.stop_loss_pct)

    def calculate_take_profit(self, entry_price: float, is_long: bool = True) -> Optional[float]:
        """
        Calculate take profit price based on strategy's take_profit_pct.

        Parameters:
        -----------
        entry_price : float
            Entry price for the position
        is_long : bool
            True for long positions, False for short positions

        Returns:
        --------
        float or None
            Take profit price, or None if take_profit_pct not set
        """
        if self.take_profit_pct is None:
            return None

        if is_long:
            return entry_price * (1 + self.take_profit_pct)
        else:
            return entry_price * (1 - self.take_profit_pct)

    @staticmethod
    def crossover(series1, series2) -> bool:
        """
        Check if series1 crossed above series2.

        Parameters:
        -----------
        series1 : array-like
            First series (e.g., fast moving average)
        series2 : array-like
            Second series (e.g., slow moving average)

        Returns:
        --------
        bool
            True if series1 just crossed above series2
        """
        return crossover(series1, series2)

    @staticmethod
    def crossunder(series1, series2) -> bool:
        """
        Check if series1 crossed below series2.

        Parameters:
        -----------
        series1 : array-like
            First series
        series2 : array-like
            Second series

        Returns:
        --------
        bool
            True if series1 just crossed below series2
        """
        return crossover(series2, series1)


# ===== COMMON INDICATOR HELPERS =====
# Use these in your strategies for cleaner code

def SMA(close_prices, period: int):
    """Simple Moving Average"""
    return talib.SMA(close_prices, timeperiod=period)


def EMA(close_prices, period: int):
    """Exponential Moving Average"""
    return talib.EMA(close_prices, timeperiod=period)


def RSI(close_prices, period: int = 14):
    """Relative Strength Index"""
    return talib.RSI(close_prices, timeperiod=period)


def MACD(close_prices, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9):
    """MACD indicator - returns (macd, signal, histogram)"""
    macd, signal, hist = talib.MACD(close_prices,
                                     fastperiod=fastperiod,
                                     slowperiod=slowperiod,
                                     signalperiod=signalperiod)
    return macd, signal, hist


def BBANDS(close_prices, period: int = 20, nbdevup: int = 2, nbdevdn: int = 2):
    """Bollinger Bands - returns (upper, middle, lower)"""
    upper, middle, lower = talib.BBANDS(close_prices,
                                         timeperiod=period,
                                         nbdevup=nbdevup,
                                         nbdevdn=nbdevdn)
    return upper, middle, lower


def ATR(high, low, close, period: int = 14):
    """Average True Range - volatility indicator"""
    return talib.ATR(high, low, close, timeperiod=period)


def ADX(high, low, close, period: int = 14):
    """Average Directional Index - trend strength"""
    return talib.ADX(high, low, close, timeperiod=period)


def STOCH(high, low, close, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3):
    """Stochastic Oscillator - returns (slowk, slowd)"""
    slowk, slowd = talib.STOCH(high, low, close,
                                fastk_period=fastk_period,
                                slowk_period=slowk_period,
                                slowd_period=slowd_period)
    return slowk, slowd