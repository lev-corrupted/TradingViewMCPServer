"""Momentum technical indicators."""

from typing import Dict, Any, List
import logging

from ..config import (
    STOCHASTIC_K_PERIOD,
    STOCHASTIC_D_PERIOD,
    STOCHASTIC_OVERBOUGHT,
    STOCHASTIC_OVERSOLD,
    FIBONACCI_LEVELS,
    ERROR_INSUFFICIENT_DATA,
)
from ..utils.formatters import safe_float, round_price

logger = logging.getLogger(__name__)


def calculate_stochastic(
    ohlcv_data: Dict[str, Any],
    k_period: int = STOCHASTIC_K_PERIOD,
    d_period: int = STOCHASTIC_D_PERIOD
) -> Dict[str, Any]:
    """
    Calculate Stochastic Oscillator properly.

    %K = (Current Close - Lowest Low) / (Highest High - Lowest Low) * 100
    %D = SMA of %K over d_period

    Args:
        ohlcv_data: OHLCV data dictionary
        k_period: Period for %K calculation
        d_period: Period for %D calculation (SMA of %K)

    Returns:
        %K, %D values and signal
    """
    candles = list(ohlcv_data.items())[:k_period + d_period]

    if len(candles) < k_period + d_period:
        return {"error": ERROR_INSUFFICIENT_DATA}

    # Calculate %K values for the last d_period periods
    k_values = []

    for i in range(d_period):
        period_candles = candles[i:i + k_period]
        highs = [safe_float(c[1].get("2. high", 0)) for c in period_candles]
        lows = [safe_float(c[1].get("3. low", 0)) for c in period_candles]
        current_close = safe_float(period_candles[0][1].get("4. close", 0))

        highest_high = max(highs) if highs else 0
        lowest_low = min(lows) if lows else 0

        if highest_high != lowest_low:
            k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        else:
            k = 50

        k_values.append(k)

    # Current %K is the first in the list
    percent_k = k_values[0]

    # %D is SMA of %K values
    percent_d = sum(k_values) / len(k_values)

    # Determine signal
    if percent_k > STOCHASTIC_OVERBOUGHT:
        signal = "OVERBOUGHT"
    elif percent_k < STOCHASTIC_OVERSOLD:
        signal = "OVERSOLD"
    else:
        signal = "NEUTRAL"

    return {
        "percent_k": round(percent_k, 2),
        "percent_d": round(percent_d, 2),
        "signal": signal,
        "interpretation": f"K={percent_k:.1f}% {'above' if percent_k > percent_d else 'below'} D={percent_d:.1f}%"
    }


def calculate_fibonacci_levels(ohlcv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate Fibonacci retracement levels.

    Args:
        ohlcv_data: OHLCV data dictionary

    Returns:
        Fibonacci levels and swing points
    """
    candles = list(ohlcv_data.items())[:100]

    if not candles:
        return {"error": ERROR_INSUFFICIENT_DATA}

    # Find swing high and swing low
    highs = [safe_float(candle[1].get("2. high", 0)) for candle in candles]
    lows = [safe_float(candle[1].get("3. low", 0)) for candle in candles]

    swing_high = max(highs) if highs else 0
    swing_low = min(lows) if lows else 0
    diff = swing_high - swing_low

    # Calculate Fibonacci retracement levels
    levels = {
        "0.0%": round_price(swing_high),
        "23.6%": round_price(swing_high - (diff * 0.236)),
        "38.2%": round_price(swing_high - (diff * 0.382)),
        "50.0%": round_price(swing_high - (diff * 0.500)),
        "61.8%": round_price(swing_high - (diff * 0.618)),
        "78.6%": round_price(swing_high - (diff * 0.786)),
        "100.0%": round_price(swing_low),
    }

    # Add extension levels
    levels["161.8%"] = round_price(swing_high - (diff * 1.618))
    levels["261.8%"] = round_price(swing_high - (diff * 2.618))

    levels["swing_high"] = swing_high
    levels["swing_low"] = swing_low
    levels["range"] = round_price(diff)

    return levels


def calculate_rsi(ohlcv_data: Dict[str, Any], period: int = 14) -> Dict[str, Any]:
    """
    Calculate Relative Strength Index (RSI).

    RSI = 100 - (100 / (1 + RS))
    RS = Average Gain / Average Loss

    Args:
        ohlcv_data: OHLCV data dictionary
        period: RSI period (default 14)

    Returns:
        RSI value and signal
    """
    candles = list(ohlcv_data.items())[:period + 10]

    if len(candles) < period + 1:
        return {"error": ERROR_INSUFFICIENT_DATA}

    closes = [safe_float(c[1].get("4. close", 0)) for c in candles]

    # Calculate price changes
    gains = []
    losses = []

    for i in range(len(closes) - 1):
        change = closes[i] - closes[i + 1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    # Calculate average gains and losses
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    # Calculate RS and RSI
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    # Determine signal
    if rsi > 70:
        signal = "OVERBOUGHT"
    elif rsi < 30:
        signal = "OVERSOLD"
    else:
        signal = "NEUTRAL"

    return {
        "rsi": round(rsi, 2),
        "signal": signal,
        "interpretation": f"RSI at {rsi:.1f} - {signal}"
    }


def calculate_cci(ohlcv_data: Dict[str, Any], period: int = 20) -> Dict[str, Any]:
    """
    Calculate Commodity Channel Index (CCI).

    CCI = (Typical Price - SMA of Typical Price) / (0.015 * Mean Deviation)
    Typical Price = (High + Low + Close) / 3

    Args:
        ohlcv_data: OHLCV data dictionary
        period: CCI period (default 20)

    Returns:
        CCI value and signal
    """
    candles = list(ohlcv_data.items())[:period + 10]

    if len(candles) < period:
        return {"error": ERROR_INSUFFICIENT_DATA}

    # Calculate typical prices
    typical_prices = []
    for candle in candles[:period]:
        high = safe_float(candle[1].get("2. high", 0))
        low = safe_float(candle[1].get("3. low", 0))
        close = safe_float(candle[1].get("4. close", 0))
        typical_price = (high + low + close) / 3
        typical_prices.append(typical_price)

    # Calculate SMA of typical prices
    sma_tp = sum(typical_prices) / len(typical_prices)

    # Calculate mean deviation
    deviations = [abs(tp - sma_tp) for tp in typical_prices]
    mean_deviation = sum(deviations) / len(deviations)

    # Calculate CCI
    current_tp = typical_prices[0]
    if mean_deviation == 0:
        cci = 0
    else:
        cci = (current_tp - sma_tp) / (0.015 * mean_deviation)

    # Determine signal
    if cci > 100:
        signal = "OVERBOUGHT"
    elif cci < -100:
        signal = "OVERSOLD"
    else:
        signal = "NEUTRAL"

    return {
        "cci": round(cci, 2),
        "signal": signal,
        "interpretation": f"CCI at {cci:.1f} - {signal} (>100 overbought, <-100 oversold)"
    }


def calculate_williams_r(ohlcv_data: Dict[str, Any], period: int = 14) -> Dict[str, Any]:
    """
    Calculate Williams %R.

    Williams %R = (Highest High - Close) / (Highest High - Lowest Low) * -100

    Args:
        ohlcv_data: OHLCV data dictionary
        period: Williams %R period (default 14)

    Returns:
        Williams %R value and signal
    """
    candles = list(ohlcv_data.items())[:period]

    if len(candles) < period:
        return {"error": ERROR_INSUFFICIENT_DATA}

    # Get highs, lows, and current close
    highs = [safe_float(c[1].get("2. high", 0)) for c in candles]
    lows = [safe_float(c[1].get("3. low", 0)) for c in candles]
    current_close = safe_float(candles[0][1].get("4. close", 0))

    highest_high = max(highs)
    lowest_low = min(lows)

    # Calculate Williams %R
    if highest_high == lowest_low:
        williams_r = -50
    else:
        williams_r = ((highest_high - current_close) / (highest_high - lowest_low)) * -100

    # Determine signal
    if williams_r > -20:
        signal = "OVERBOUGHT"
    elif williams_r < -80:
        signal = "OVERSOLD"
    else:
        signal = "NEUTRAL"

    return {
        "williams_r": round(williams_r, 2),
        "signal": signal,
        "interpretation": f"Williams %R at {williams_r:.1f}% - {signal} (>-20 overbought, <-80 oversold)"
    }
