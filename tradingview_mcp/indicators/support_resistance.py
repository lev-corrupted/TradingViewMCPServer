"""Support and resistance detection indicators."""

from typing import Dict, Any, List
import logging

from ..config import (
    RECENT_CANDLES_FOR_ANALYSIS,
    GAPS_DETECTION_CANDLES,
    ERROR_INSUFFICIENT_DATA,
)
from ..utils.formatters import safe_float, round_price

logger = logging.getLogger(__name__)


def detect_support_resistance(ohlcv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect support and resistance levels using local extrema.

    Args:
        ohlcv_data: OHLCV data dictionary

    Returns:
        Support and resistance levels
    """
    candles = list(ohlcv_data.items())[:RECENT_CANDLES_FOR_ANALYSIS]

    if len(candles) < 5:
        return {"error": ERROR_INSUFFICIENT_DATA}

    highs = [safe_float(c[1].get("2. high", 0)) for c in candles]
    lows = [safe_float(c[1].get("3. low", 0)) for c in candles]

    resistance_levels = []
    support_levels = []

    # Find local maxima and minima (requires at least 2 candles on each side)
    for i in range(2, len(candles) - 2):
        # Resistance: local maximum
        if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and
            highs[i] > highs[i+1] and highs[i] > highs[i+2]):
            resistance_levels.append(highs[i])

        # Support: local minimum
        if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and
            lows[i] < lows[i+1] and lows[i] < lows[i+2]):
            support_levels.append(lows[i])

    # Remove duplicates and sort
    resistance_levels = sorted(set(resistance_levels), reverse=True)[:3]
    support_levels = sorted(set(support_levels))[:3]

    current_price = safe_float(candles[0][1].get("4. close", 0))

    return {
        "resistance_levels": [round_price(r) for r in resistance_levels],
        "support_levels": [round_price(s) for s in support_levels],
        "current_price": round_price(current_price),
        "interpretation": "Key levels where price has historically reversed or consolidated"
    }


def calculate_pivot_points(ohlcv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate pivot points (Standard method).

    Pivot = (High + Low + Close) / 3
    R1 = (2 * Pivot) - Low
    R2 = Pivot + (High - Low)
    R3 = High + 2 * (Pivot - Low)
    S1 = (2 * Pivot) - High
    S2 = Pivot - (High - Low)
    S3 = Low - 2 * (High - Pivot)

    Args:
        ohlcv_data: OHLCV data dictionary

    Returns:
        Pivot points (pivot, R1-R3, S1-S3)
    """
    candles = list(ohlcv_data.items())[:1]

    if not candles:
        return {"error": ERROR_INSUFFICIENT_DATA}

    high = safe_float(candles[0][1].get("2. high", 0))
    low = safe_float(candles[0][1].get("3. low", 0))
    close = safe_float(candles[0][1].get("4. close", 0))

    # Standard Pivot Points
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    r2 = pivot + (high - low)
    r3 = high + 2 * (pivot - low)
    s1 = (2 * pivot) - high
    s2 = pivot - (high - low)
    s3 = low - 2 * (high - pivot)

    return {
        "pivot": round_price(pivot),
        "resistance_1": round_price(r1),
        "resistance_2": round_price(r2),
        "resistance_3": round_price(r3),
        "support_1": round_price(s1),
        "support_2": round_price(s2),
        "support_3": round_price(s3),
        "interpretation": "Pivot points for today's trading - R1/S1 are primary, R2/S2 secondary targets"
    }


def calculate_fibonacci_pivot_points(ohlcv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate Fibonacci pivot points.

    Args:
        ohlcv_data: OHLCV data dictionary

    Returns:
        Fibonacci pivot points
    """
    candles = list(ohlcv_data.items())[:1]

    if not candles:
        return {"error": ERROR_INSUFFICIENT_DATA}

    high = safe_float(candles[0][1].get("2. high", 0))
    low = safe_float(candles[0][1].get("3. low", 0))
    close = safe_float(candles[0][1].get("4. close", 0))

    # Fibonacci Pivot Points
    pivot = (high + low + close) / 3
    r1 = pivot + 0.382 * (high - low)
    r2 = pivot + 0.618 * (high - low)
    r3 = pivot + 1.000 * (high - low)
    s1 = pivot - 0.382 * (high - low)
    s2 = pivot - 0.618 * (high - low)
    s3 = pivot - 1.000 * (high - low)

    return {
        "pivot": round_price(pivot),
        "resistance_1": round_price(r1),
        "resistance_2": round_price(r2),
        "resistance_3": round_price(r3),
        "support_1": round_price(s1),
        "support_2": round_price(s2),
        "support_3": round_price(s3),
        "type": "Fibonacci"
    }


def detect_gaps(ohlcv_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detect unfilled price gaps.

    Gap Up: Current low > Previous high
    Gap Down: Current high < Previous low

    Args:
        ohlcv_data: OHLCV data dictionary

    Returns:
        List of detected gaps
    """
    candles = list(ohlcv_data.items())[:GAPS_DETECTION_CANDLES]

    if len(candles) < 2:
        return []

    gaps = []

    for i in range(1, len(candles)):
        current_time, current = candles[i]
        prev_time, prev = candles[i-1]

        current_low = safe_float(current.get("3. low", 0))
        current_high = safe_float(current.get("2. high", 0))
        prev_low = safe_float(prev.get("3. low", 0))
        prev_high = safe_float(prev.get("2. high", 0))

        # Gap up: current low > previous high
        if current_low > prev_high:
            gap_size = current_low - prev_high
            gaps.append({
                "type": "gap_up",
                "size": round_price(gap_size),
                "from_price": round_price(prev_high),
                "to_price": round_price(current_low),
                "timestamp": current_time,
                "filled": False
            })

        # Gap down: current high < previous low
        elif current_high < prev_low:
            gap_size = prev_low - current_high
            gaps.append({
                "type": "gap_down",
                "size": round_price(gap_size),
                "from_price": round_price(prev_low),
                "to_price": round_price(current_high),
                "timestamp": current_time,
                "filled": False
            })

    return gaps


def identify_swing_points(ohlcv_data: Dict[str, Any], lookback: int = 5) -> Dict[str, Any]:
    """
    Identify swing highs and swing lows.

    Swing High: High that is higher than lookback bars on each side
    Swing Low: Low that is lower than lookback bars on each side

    Args:
        ohlcv_data: OHLCV data dictionary
        lookback: Number of bars to look on each side

    Returns:
        Swing highs and lows
    """
    candles = list(ohlcv_data.items())[:50]

    if len(candles) < lookback * 2 + 1:
        return {"error": ERROR_INSUFFICIENT_DATA}

    highs = [safe_float(c[1].get("2. high", 0)) for c in candles]
    lows = [safe_float(c[1].get("3. low", 0)) for c in candles]

    swing_highs = []
    swing_lows = []

    for i in range(lookback, len(candles) - lookback):
        # Check if it's a swing high
        is_swing_high = all(highs[i] > highs[i-j] for j in range(1, lookback + 1))
        is_swing_high = is_swing_high and all(highs[i] > highs[i+j] for j in range(1, lookback + 1))

        if is_swing_high:
            swing_highs.append({
                "price": round_price(highs[i]),
                "index": i,
                "timestamp": candles[i][0]
            })

        # Check if it's a swing low
        is_swing_low = all(lows[i] < lows[i-j] for j in range(1, lookback + 1))
        is_swing_low = is_swing_low and all(lows[i] < lows[i+j] for j in range(1, lookback + 1))

        if is_swing_low:
            swing_lows.append({
                "price": round_price(lows[i]),
                "index": i,
                "timestamp": candles[i][0]
            })

    return {
        "swing_highs": swing_highs[:5],  # Most recent 5
        "swing_lows": swing_lows[:5],    # Most recent 5
        "interpretation": "Swing points represent local trend reversals"
    }
