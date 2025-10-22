"""Volume-based technical indicators."""

import logging
from typing import Any, Dict, List

from ..config import (
    ERROR_INSUFFICIENT_DATA,
    MARKET_PROFILE_CANDLES,
    RECENT_CANDLES_FOR_ANALYSIS,
    VOLUME_PROFILE_LEVELS,
    VOLUME_PROFILE_VALUE_AREA,
)
from ..utils.formatters import round_price, safe_float

logger = logging.getLogger(__name__)


def calculate_vwap(
    ohlcv_data: Dict[str, Any], num_candles: int = RECENT_CANDLES_FOR_ANALYSIS
) -> float:
    """
    Calculate VWAP (Volume Weighted Average Price).

    VWAP = Σ(Typical Price * Volume) / Σ(Volume)
    Typical Price = (High + Low + Close) / 3

    Args:
        ohlcv_data: OHLCV data dictionary
        num_candles: Number of candles to use

    Returns:
        VWAP value
    """
    candles = list(ohlcv_data.items())[:num_candles]

    total_pv = 0
    total_volume = 0

    for timestamp, values in candles:
        high = safe_float(values.get("2. high", 0))
        low = safe_float(values.get("3. low", 0))
        close = safe_float(values.get("4. close", 0))
        volume = safe_float(values.get("5. volume", 1))

        # Use 1 as minimum volume for forex (often no volume data)
        volume = max(volume, 1)

        # Typical price
        typical_price = (high + low + close) / 3

        total_pv += typical_price * volume
        total_volume += volume

    return total_pv / total_volume if total_volume > 0 else 0


def calculate_volume_profile(
    ohlcv_data: Dict[str, Any], num_levels: int = VOLUME_PROFILE_LEVELS
) -> Dict[str, Any]:
    """
    Calculate volume profile (volume at price levels).

    Args:
        ohlcv_data: OHLCV data dictionary
        num_levels: Number of price levels to create

    Returns:
        Volume profile with POC and volume nodes
    """
    candles = list(ohlcv_data.items())[:RECENT_CANDLES_FOR_ANALYSIS]

    if not candles:
        return {"error": ERROR_INSUFFICIENT_DATA}

    # Collect price and volume data
    price_volume: List[Dict[str, float]] = []

    for timestamp, values in candles:
        high = safe_float(values.get("2. high", 0))
        low = safe_float(values.get("3. low", 0))
        close = safe_float(values.get("4. close", 0))
        volume = safe_float(values.get("5. volume", 1))

        price_volume.append({"price": close, "volume": max(volume, 1)})

    # Find price range
    prices = [pv["price"] for pv in price_volume]
    min_price = min(prices)
    max_price = max(prices)
    price_step = (
        (max_price - min_price) / num_levels if max_price > min_price else 0.0001
    )

    # Create price levels and distribute volume
    levels: Dict[float, float] = {}

    for i in range(num_levels):
        level_price = min_price + (i * price_step)
        levels[round_price(level_price)] = 0

    # Distribute volume to closest level
    for pv in price_volume:
        price = pv["price"]
        volume = pv["volume"]

        # Find closest level
        closest_level = min(levels.keys(), key=lambda x: abs(x - price))
        levels[closest_level] += volume

    # Find POC (Point of Control - highest volume level)
    poc_price = max(levels.items(), key=lambda x: x[1])[0] if levels else 0

    # Find high and low volume nodes
    sorted_levels = sorted(levels.items(), key=lambda x: x[1], reverse=True)
    high_volume_nodes = [
        {"price": p, "volume": round(v, 2)} for p, v in sorted_levels[:3]
    ]
    low_volume_nodes = [
        {"price": p, "volume": round(v, 2)} for p, v in sorted_levels[-3:]
    ]

    return {
        "poc": poc_price,
        "high_volume_nodes": high_volume_nodes,
        "low_volume_nodes": low_volume_nodes,
        "price_levels": {str(k): round(v, 2) for k, v in levels.items()},
        "min_price": min_price,
        "max_price": max_price,
    }


def calculate_market_profile(ohlcv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate market profile with TPO, POC, and value areas.

    TPO (Time Price Opportunity) represents time spent at price levels.

    Args:
        ohlcv_data: OHLCV data dictionary

    Returns:
        Market profile with POC and value areas
    """
    candles = list(ohlcv_data.items())[:MARKET_PROFILE_CANDLES]

    if not candles:
        return {"error": ERROR_INSUFFICIENT_DATA}

    tpo_count: Dict[float, int] = {}

    # Count TPOs at each price level
    for timestamp, values in candles:
        high = safe_float(values.get("2. high", 0))
        low = safe_float(values.get("3. low", 0))

        # Create price levels within the candle range
        price_range = high - low
        num_ticks = max(int(price_range * 10000), 1)  # Adjust for precision

        for i in range(num_ticks + 1):
            price = low + (i * price_range / num_ticks)
            price_key = round_price(price)
            tpo_count[price_key] = tpo_count.get(price_key, 0) + 1

    if not tpo_count:
        return {"error": ERROR_INSUFFICIENT_DATA}

    # Find POC (Point of Control - most TPOs)
    poc = max(tpo_count.items(), key=lambda x: x[1])[0]

    # Calculate value area (70% of TPOs around POC)
    total_tpos = sum(tpo_count.values())
    target_tpos = total_tpos * VOLUME_PROFILE_VALUE_AREA

    sorted_prices = sorted(tpo_count.items(), key=lambda x: x[1], reverse=True)

    value_area_prices = []
    accumulated_tpos = 0

    for price, count in sorted_prices:
        value_area_prices.append(price)
        accumulated_tpos += count
        if accumulated_tpos >= target_tpos:
            break

    vah = max(value_area_prices) if value_area_prices else poc  # Value Area High
    val = min(value_area_prices) if value_area_prices else poc  # Value Area Low

    return {
        "poc": poc,
        "value_area_high": vah,
        "value_area_low": val,
        "tpo_count": len(tpo_count),
        "profile_range": {"high": max(tpo_count.keys()), "low": min(tpo_count.keys())},
        "interpretation": f"POC at {poc:.5f}. Value area: {val:.5f} to {vah:.5f}. "
        f"Price typically trades 70% of time within value area.",
    }


def calculate_obv(ohlcv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate On-Balance Volume (OBV).

    OBV increases by volume when price closes higher, decreases when price closes lower.

    Args:
        ohlcv_data: OHLCV data dictionary

    Returns:
        OBV value and trend
    """
    candles = list(ohlcv_data.items())[:100]

    if len(candles) < 2:
        return {"error": ERROR_INSUFFICIENT_DATA}

    obv = 0
    obv_values = []

    for i in range(len(candles) - 1):
        current_close = safe_float(candles[i][1].get("4. close", 0))
        prev_close = safe_float(candles[i + 1][1].get("4. close", 0))
        volume = safe_float(candles[i][1].get("5. volume", 1))

        if current_close > prev_close:
            obv += volume
        elif current_close < prev_close:
            obv -= volume

        obv_values.append(obv)

    # Determine trend from recent OBV movement
    if len(obv_values) >= 10:
        recent_obv = obv_values[:10]
        if recent_obv[0] > recent_obv[5]:
            trend = "RISING"
        elif recent_obv[0] < recent_obv[5]:
            trend = "FALLING"
        else:
            trend = "FLAT"
    else:
        trend = "UNKNOWN"

    return {
        "obv": round(obv, 2),
        "trend": trend,
        "interpretation": f"OBV is {trend} - {'bullish' if trend == 'RISING' else 'bearish' if trend == 'FALLING' else 'neutral'} volume pressure",
    }
