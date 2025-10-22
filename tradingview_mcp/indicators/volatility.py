"""Volatility technical indicators."""

import logging
import math
from typing import Any, Dict

from ..config import ATR_PERIOD, BB_PERIOD, BB_STD_DEV, ERROR_INSUFFICIENT_DATA
from ..utils.formatters import round_price, safe_float

logger = logging.getLogger(__name__)


def calculate_bollinger_bands(
    ohlcv_data: Dict[str, Any], period: int = BB_PERIOD, std_dev: int = BB_STD_DEV
) -> Dict[str, Any]:
    """
    Calculate Bollinger Bands.

    Middle Band = SMA(period)
    Upper Band = Middle Band + (std_dev * standard deviation)
    Lower Band = Middle Band - (std_dev * standard deviation)

    Args:
        ohlcv_data: OHLCV data dictionary
        period: Period for SMA calculation
        std_dev: Number of standard deviations

    Returns:
        Upper, middle, lower bands and %B indicator
    """
    candles = list(ohlcv_data.items())[: period + 10]

    if len(candles) < period:
        return {"error": ERROR_INSUFFICIENT_DATA}

    closes = [safe_float(c[1].get("4. close", 0)) for c in candles]

    # Calculate SMA (middle band)
    sma = sum(closes[:period]) / period

    # Calculate standard deviation
    variance = sum((x - sma) ** 2 for x in closes[:period]) / period
    std = math.sqrt(variance)

    # Calculate bands
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)

    current_price = closes[0]

    # Calculate %B (position within bands)
    if upper_band != lower_band:
        percent_b = (current_price - lower_band) / (upper_band - lower_band)
    else:
        percent_b = 0.5

    # Calculate bandwidth
    bandwidth = upper_band - lower_band

    # Determine signal
    if percent_b > 1:
        signal = "OVERBOUGHT"
    elif percent_b < 0:
        signal = "OVERSOLD"
    else:
        signal = "NORMAL"

    return {
        "upper_band": round_price(upper_band),
        "middle_band": round_price(sma),
        "lower_band": round_price(lower_band),
        "current_price": round_price(current_price),
        "bandwidth": round_price(bandwidth),
        "percent_b": round(percent_b, 3),
        "signal": signal,
        "interpretation": f"Price at {percent_b * 100:.1f}% of band width - {signal}",
    }


def calculate_atr(
    ohlcv_data: Dict[str, Any], period: int = ATR_PERIOD
) -> Dict[str, Any]:
    """
    Calculate Average True Range (ATR).

    True Range = max(high - low, |high - prev_close|, |low - prev_close|)
    ATR = Average of True Range over period

    Args:
        ohlcv_data: OHLCV data dictionary
        period: ATR period

    Returns:
        ATR value and percentage
    """
    candles = list(ohlcv_data.items())[: period + 10]

    if len(candles) < period + 1:
        return {"error": ERROR_INSUFFICIENT_DATA}

    true_ranges = []

    for i in range(len(candles) - 1):
        high = safe_float(candles[i][1].get("2. high", 0))
        low = safe_float(candles[i][1].get("3. low", 0))
        prev_close = safe_float(candles[i + 1][1].get("4. close", 0))

        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        true_ranges.append(tr)

    # Calculate ATR (average of true ranges)
    atr = sum(true_ranges[:period]) / period

    current_price = safe_float(candles[0][1].get("4. close", 1))
    atr_percent = (atr / current_price) * 100 if current_price > 0 else 0

    # Volatility classification
    if atr_percent > 3:
        volatility = "HIGH"
    elif atr_percent > 1.5:
        volatility = "MODERATE"
    else:
        volatility = "LOW"

    return {
        "atr": round_price(atr),
        "atr_percent": round(atr_percent, 2),
        "volatility": volatility,
        "interpretation": f"ATR shows {atr_percent:.2f}% volatility ({volatility}) - use for stop loss and position sizing",
    }


def calculate_keltner_channels(
    ohlcv_data: Dict[str, Any], period: int = 20, atr_multiplier: float = 2.0
) -> Dict[str, Any]:
    """
    Calculate Keltner Channels.

    Middle Line = EMA(period)
    Upper Channel = EMA + (ATR * multiplier)
    Lower Channel = EMA - (ATR * multiplier)

    Args:
        ohlcv_data: OHLCV data dictionary
        period: EMA period
        atr_multiplier: ATR multiplier for channels

    Returns:
        Upper, middle, lower channels
    """
    candles = list(ohlcv_data.items())[: period * 2]

    if len(candles) < period + 10:
        return {"error": ERROR_INSUFFICIENT_DATA}

    closes = [safe_float(c[1].get("4. close", 0)) for c in candles]

    # Calculate EMA for middle line
    from .trend import calculate_ema

    ema = calculate_ema(closes, period)

    # Calculate ATR
    atr_result = calculate_atr(ohlcv_data, period)
    if "error" in atr_result:
        return atr_result

    atr = atr_result["atr"]

    # Calculate channels
    upper_channel = ema + (atr * atr_multiplier)
    lower_channel = ema - (atr * atr_multiplier)

    current_price = closes[0]

    return {
        "upper_channel": round_price(upper_channel),
        "middle_line": round_price(ema),
        "lower_channel": round_price(lower_channel),
        "current_price": round_price(current_price),
        "width": round_price(upper_channel - lower_channel),
    }
