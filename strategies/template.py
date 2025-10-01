"""
Strategy Template - Copy this to create new strategies!

How to use:
1. Copy this file: cp strategies/template.py strategies/your_strategy.py
2. Rename the class from TemplateStrategy to YourStrategy
3. Update the docstring to describe what your strategy does
4. Define your parameters
5. Fill in init() with indicator calculations
6. Fill in next() with trading logic
7. Run strategy_manager.py - your strategy will be auto-discovered!
"""

from strategies.base_strategy import BaseStrategy
import talib


class TemplateStrategy(BaseStrategy):
    """
    [DESCRIBE YOUR STRATEGY HERE]

    Example:
    This strategy buys when RSI crosses below 30 (oversold)
    and sells when RSI crosses above 70 (overbought).
    """

    # ===== PARAMETERS =====
    # Define your strategy parameters here
    # These can be optimized later

    # Example parameters:
    # rsi_period = 14
    # rsi_oversold = 30
    # rsi_overbought = 70
    # sma_period = 50

    # Optional: Set risk management defaults
    # stop_loss_pct = 0.02  # 2% stop loss
    # take_profit_pct = 0.04  # 4% take profit
    # position_size = 1.0  # Use full equity

    def init(self):
        """
        Calculate your indicators here.

        Use self.I() to register indicators with the backtesting engine.
        This makes them visible in the output chart.

        Example:
        --------
        # Calculate RSI
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)

        # Calculate moving averages
        self.sma = self.I(talib.SMA, self.data.Close, self.sma_period)
        self.ema = self.I(talib.EMA, self.data.Close, 20)

        # Calculate MACD
        self.macd, self.signal, self.hist = self.I(
            talib.MACD,
            self.data.Close,
            fastperiod=12,
            slowperiod=26,
            signalperiod=9
        )

        # Calculate Bollinger Bands
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(
            talib.BBANDS,
            self.data.Close,
            timeperiod=20,
            nbdevup=2,
            nbdevdn=2
        )
        """
        # YOUR INDICATOR CALCULATIONS GO HERE
        pass

    def next(self):
        """
        Your trading logic goes here.

        This method is called for each bar in the data.
        Use self.position to check current position state.
        Use self.buy() / self.sell() / self.position.close() to trade.

        Access current and previous data:
        - self.data.Close[-1]  # Current close price
        - self.data.Close[-2]  # Previous close price
        - self.rsi[-1]  # Current RSI value (if calculated in init)

        Example:
        --------
        # Simple RSI strategy
        if self.rsi[-1] < self.rsi_oversold and not self.position:
            # Buy when oversold and no position
            self.buy()

        elif self.rsi[-1] > self.rsi_overbought and self.position:
            # Sell when overbought and have position
            self.position.close()

        # MA crossover strategy
        if self.crossover(self.fast_ma, self.slow_ma):
            if not self.position:
                self.buy()
        elif self.crossunder(self.fast_ma, self.slow_ma):
            if self.position:
                self.position.close()

        # With stop loss and take profit
        if buy_condition and not self.position:
            price = self.data.Close[-1]
            self.buy_with_sl_tp(
                stop_loss=price * 0.98,  # 2% stop loss
                take_profit=price * 1.04  # 4% take profit
            )
        """
        # YOUR TRADING LOGIC GOES HERE
        pass


# ===== HELPER FUNCTIONS (OPTIONAL) =====
# You can define additional helper functions here if needed

def example_helper_function(data):
    """
    Example helper function.
    Put any complex calculations here to keep next() clean.
    """
    pass