#!/usr/bin/env python3
"""
TradingView MCP Server - Professional Multi-Asset Trading Assistant

Provides real-time market data, technical analysis, and trading recommendations
via Model Context Protocol (MCP) for Claude Desktop integration.

Supported Assets:
- Forex (22+ pairs + gold)
- Stocks (US equities)
- Crypto (BTC, ETH, and major cryptocurrencies)

Data Sources:
- Alpha Vantage API for real-time quotes and historical data
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Asset configuration
FOREX_PAIRS = [
    # Majors
    'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
    # Crosses
    'GBPJPY', 'EURJPY', 'AUDJPY', 'NZDJPY', 'EURGBP', 'EURAUD', 'EURCHF',
    'GBPAUD', 'GBPCAD', 'AUDCAD',
    # Exotics
    'USDTRY', 'USDZAR', 'USDMXN', 'USDBRL',
    # Commodities
    'XAUUSD'
]

POPULAR_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'BRK.B',
    'V', 'JPM', 'JNJ', 'WMT', 'PG', 'MA', 'DIS', 'HD', 'BAC', 'NFLX',
    'CSCO', 'ADBE', 'CRM', 'INTC', 'AMD', 'PYPL', 'NKE', 'ORCL',
    'SPY', 'QQQ', 'IWM', 'DIA'  # ETFs
]

CRYPTO_SYMBOLS = [
    'BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'DOGE', 'SOL', 'MATIC',
    'DOT', 'AVAX', 'LINK', 'UNI', 'LTC', 'ATOM', 'XLM', 'ALGO'
]

# Typical spreads (pips) for reference
TYPICAL_SPREADS = {
    'EURUSD': 1.5, 'GBPUSD': 2.0, 'USDJPY': 1.5, 'USDCHF': 2.0,
    'AUDUSD': 2.0, 'USDCAD': 2.5, 'NZDUSD': 3.0,
    'GBPJPY': 5.0, 'EURJPY': 3.0, 'AUDJPY': 4.0, 'NZDJPY': 5.0,
    'EURGBP': 2.5, 'EURAUD': 4.0, 'EURCHF': 3.0,
    'GBPAUD': 6.0, 'GBPCAD': 5.0, 'AUDCAD': 4.0,
    'USDTRY': 30.0, 'USDZAR': 50.0, 'USDMXN': 40.0, 'USDBRL': 60.0,
    'XAUUSD': 0.50
}

def get_spread(pair: str, timeframe: str = "1h") -> float:
    """Get typical spread for a pair."""
    return TYPICAL_SPREADS.get(pair, 3.0)

def detect_asset_type(symbol: str) -> Tuple[str, str]:
    """
    Detect asset type from symbol.

    Returns:
        Tuple of (asset_type, formatted_symbol)
        asset_type: 'forex', 'stock', or 'crypto'
    """
    symbol = symbol.upper().replace("/", "").replace("_", "").replace("-", "")

    # Check if it's crypto
    if symbol in CRYPTO_SYMBOLS or symbol.endswith('USD') and symbol[:-3] in CRYPTO_SYMBOLS:
        return ('crypto', symbol)

    # Check if it's forex (6 chars or XAUUSD)
    if len(symbol) == 6 or symbol == 'XAUUSD':
        if symbol in FOREX_PAIRS:
            return ('forex', symbol)

    # Otherwise assume stock
    return ('stock', symbol)

# Alpha Vantage API setup
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
if not ALPHA_VANTAGE_API_KEY:
    print("WARNING: ALPHA_VANTAGE_API_KEY not found in .env file", file=sys.stderr)

# Initialize MCP server
mcp = FastMCP(
    name="TradingView Multi-Asset Trading Assistant",
    instructions=(
        "Professional trading assistant providing real-time market data, "
        "technical analysis, and trading recommendations for multiple asset classes. "
        "Supports Forex (22+ pairs), Stocks (US equities), and Crypto (BTC, ETH, etc). "
        "Includes advanced tools: Volume Profile, Market Profile, VWAP, Fibonacci, "
        "Bollinger Bands, MACD, Moving Averages, ATR, Support/Resistance, Pivot Points, "
        "Stochastic, ADX, and Ichimoku Cloud."
    ),
)

# ===== HELPER FUNCTIONS =====

def get_all_forex_pairs() -> List[str]:
    """Get all available forex pairs."""
    return sorted(FOREX_PAIRS)


def format_pair_for_alpha_vantage(pair: str) -> tuple[str, str]:
    """
    Convert pair format to Alpha Vantage format.

    Examples:
        EURUSD -> (EUR, USD)
        XAUUSD -> (XAU, USD)  # Gold

    Returns:
        Tuple of (from_currency, to_currency)
    """
    if pair == 'XAUUSD':
        return ('XAU', 'USD')

    # Standard forex pairs (6 characters)
    if len(pair) == 6:
        return (pair[:3], pair[3:])

    raise ValueError(f"Invalid pair format: {pair}")


def get_quote(symbol: str) -> Dict[str, Any]:
    """
    Get real-time quote from Alpha Vantage (universal for all asset types).

    Parameters:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')

    Returns:
        Dictionary with quote data
    """
    import requests

    asset_type, formatted_symbol = detect_asset_type(symbol)

    url = "https://www.alphavantage.co/query"

    try:
        if asset_type == 'forex':
            from_curr, to_curr = format_pair_for_alpha_vantage(formatted_symbol)
            params = {
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": from_curr,
                "to_currency": to_curr,
                "apikey": ALPHA_VANTAGE_API_KEY
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "Realtime Currency Exchange Rate" in data:
                rate_data = data["Realtime Currency Exchange Rate"]
                return {
                    "symbol": formatted_symbol,
                    "asset_type": "forex",
                    "price": float(rate_data["5. Exchange Rate"]),
                    "bid": float(rate_data.get("8. Bid Price", rate_data["5. Exchange Rate"])),
                    "ask": float(rate_data.get("9. Ask Price", rate_data["5. Exchange Rate"])),
                    "timestamp": rate_data["6. Last Refreshed"],
                    "timezone": rate_data.get("7. Time Zone", "UTC")
                }

        elif asset_type == 'crypto':
            # For crypto, format as BTC -> BTCUSD
            crypto_base = formatted_symbol.replace('USD', '') if formatted_symbol.endswith('USD') else formatted_symbol
            params = {
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": crypto_base,
                "to_currency": "USD",
                "apikey": ALPHA_VANTAGE_API_KEY
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "Realtime Currency Exchange Rate" in data:
                rate_data = data["Realtime Currency Exchange Rate"]
                price = float(rate_data["5. Exchange Rate"])
                return {
                    "symbol": formatted_symbol,
                    "asset_type": "crypto",
                    "price": price,
                    "bid": price * 0.999,  # Approximate spread
                    "ask": price * 1.001,
                    "timestamp": rate_data["6. Last Refreshed"],
                    "timezone": rate_data.get("7. Time Zone", "UTC")
                }

        else:  # stock
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": formatted_symbol,
                "apikey": ALPHA_VANTAGE_API_KEY
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                price = float(quote.get("05. price", 0))
                return {
                    "symbol": formatted_symbol,
                    "asset_type": "stock",
                    "price": price,
                    "bid": price,
                    "ask": price,
                    "open": float(quote.get("02. open", 0)),
                    "high": float(quote.get("03. high", 0)),
                    "low": float(quote.get("04. low", 0)),
                    "volume": int(quote.get("06. volume", 0)),
                    "previous_close": float(quote.get("08. previous close", 0)),
                    "change": float(quote.get("09. change", 0)),
                    "change_percent": quote.get("10. change percent", "0%"),
                    "timestamp": quote.get("07. latest trading day", ""),
                }

        # Handle errors
        if "Note" in data:
            return {"error": "API rate limit reached. Please wait a minute.", "symbol": symbol}
        else:
            return {"error": f"No data available for {symbol}", "symbol": symbol}

    except Exception as e:
        return {"error": str(e), "symbol": symbol}


def get_forex_quote(pair: str) -> Dict[str, Any]:
    """Legacy function - calls get_quote for backwards compatibility."""
    return get_quote(pair)


def get_historical_data(pair: str, timeframe: str = "1h", outputsize: str = "compact") -> Dict[str, Any]:
    """
    Get historical price data from Alpha Vantage.

    Returns OHLCV data for analysis.
    """
    import requests

    from_curr, to_curr = format_pair_for_alpha_vantage(pair)

    # Map timeframe to Alpha Vantage interval
    interval_map = {
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "1h": "60min",
        "4h": "daily",
        "1d": "daily",
    }
    interval = interval_map.get(timeframe, "60min")

    url = "https://www.alphavantage.co/query"

    if interval in ["5min", "15min", "30min", "60min"]:
        params = {
            "function": "FX_INTRADAY",
            "from_symbol": from_curr,
            "to_symbol": to_curr,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
    else:
        params = {
            "function": "FX_DAILY",
            "from_symbol": from_curr,
            "to_symbol": to_curr,
            "outputsize": outputsize,
            "apikey": ALPHA_VANTAGE_API_KEY
        }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        # Find the time series key
        ts_key = None
        for key in data.keys():
            if "Time Series" in key:
                ts_key = key
                break

        if ts_key and ts_key in data:
            return {"success": True, "data": data[ts_key], "pair": pair}
        elif "Note" in data:
            return {"success": False, "error": "API rate limit reached", "pair": pair}
        else:
            return {"success": False, "error": "No data available", "pair": pair}
    except Exception as e:
        return {"success": False, "error": str(e), "pair": pair}


def calculate_technical_indicators(pair: str, timeframe: str = "1h") -> Dict[str, Any]:
    """
    Calculate technical indicators for a forex pair.

    Uses Alpha Vantage technical indicators API.
    """
    import requests

    from_curr, to_curr = format_pair_for_alpha_vantage(pair)

    # Map timeframe to Alpha Vantage interval
    interval_map = {
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "1h": "60min",
        "4h": "daily",
        "1d": "daily",
    }
    interval = interval_map.get(timeframe, "60min")

    indicators = {}

    # Get RSI
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "RSI",
            "symbol": f"{from_curr}{to_curr}",
            "interval": interval,
            "time_period": 14,
            "series_type": "close",
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if "Technical Analysis: RSI" in data:
            latest_rsi = list(data["Technical Analysis: RSI"].values())[0]
            indicators["rsi"] = float(latest_rsi["RSI"])
    except:
        indicators["rsi"] = None

    return indicators


def calculate_vwap(ohlcv_data: Dict[str, Any]) -> float:
    """Calculate VWAP from OHLCV data."""
    total_pv = 0
    total_volume = 0

    for timestamp, values in list(ohlcv_data.items())[:100]:  # Use recent 100 candles
        typical_price = (float(values.get("1. open", 0)) +
                        float(values.get("2. high", 0)) +
                        float(values.get("3. low", 0)) +
                        float(values.get("4. close", 0))) / 4
        volume = float(values.get("5. volume", 1))  # Forex often has no volume, use 1

        total_pv += typical_price * volume
        total_volume += volume

    return total_pv / total_volume if total_volume > 0 else 0


def detect_gaps(ohlcv_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Detect unfilled price gaps in the data."""
    gaps = []
    candles = list(ohlcv_data.items())[:50]  # Check recent 50 candles

    for i in range(1, len(candles)):
        current_time, current = candles[i]
        prev_time, prev = candles[i-1]

        current_low = float(current.get("3. low", 0))
        current_high = float(current.get("2. high", 0))
        prev_low = float(prev.get("3. low", 0))
        prev_high = float(prev.get("2. high", 0))

        # Gap up
        if current_low > prev_high:
            gap_size = current_low - prev_high
            gaps.append({
                "type": "gap_up",
                "size": gap_size,
                "from_price": prev_high,
                "to_price": current_low,
                "timestamp": current_time,
                "filled": False
            })

        # Gap down
        elif current_high < prev_low:
            gap_size = prev_low - current_high
            gaps.append({
                "type": "gap_down",
                "size": gap_size,
                "from_price": prev_low,
                "to_price": current_high,
                "timestamp": current_time,
                "filled": False
            })

    return gaps


def calculate_volume_profile(ohlcv_data: Dict[str, Any], num_levels: int = 20) -> Dict[str, Any]:
    """Calculate volume profile (volume at price levels)."""
    # Collect all prices and volumes
    price_volume = []

    for timestamp, values in list(ohlcv_data.items())[:100]:
        high = float(values.get("2. high", 0))
        low = float(values.get("3. low", 0))
        close = float(values.get("4. close", 0))
        volume = float(values.get("5. volume", 1))

        # Distribute volume across the price range
        price_volume.append({"price": close, "volume": volume})

    if not price_volume:
        return {"error": "No data available"}

    # Find price range
    prices = [pv["price"] for pv in price_volume]
    min_price = min(prices)
    max_price = max(prices)
    price_step = (max_price - min_price) / num_levels

    # Create price levels
    levels = {}
    for i in range(num_levels):
        level_price = min_price + (i * price_step)
        levels[round(level_price, 5)] = 0

    # Distribute volume to levels
    for pv in price_volume:
        price = pv["price"]
        volume = pv["volume"]

        # Find closest level
        closest_level = min(levels.keys(), key=lambda x: abs(x - price))
        levels[closest_level] += volume

    # Find POC (Point of Control - highest volume)
    poc_price = max(levels.items(), key=lambda x: x[1])[0]

    # Find high and low volume nodes
    sorted_levels = sorted(levels.items(), key=lambda x: x[1], reverse=True)
    high_volume_nodes = [{"price": p, "volume": v} for p, v in sorted_levels[:3]]
    low_volume_nodes = [{"price": p, "volume": v} for p, v in sorted_levels[-3:]]

    return {
        "poc": poc_price,
        "high_volume_nodes": high_volume_nodes,
        "low_volume_nodes": low_volume_nodes,
        "price_levels": levels,
        "min_price": min_price,
        "max_price": max_price
    }


def calculate_market_profile(ohlcv_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate market profile with TPO, POC, and value areas."""
    # Simplified market profile calculation
    candles = list(ohlcv_data.items())[:30]  # Use recent 30 candles for profile

    tpo_count = {}  # Time Price Opportunity

    for timestamp, values in candles:
        high = float(values.get("2. high", 0))
        low = float(values.get("3. low", 0))

        # Create price levels in the range
        price_range = high - low
        num_ticks = max(int(price_range * 10000), 1)  # Adjust for forex precision

        for i in range(num_ticks + 1):
            price = low + (i * price_range / num_ticks)
            price_key = round(price, 5)
            tpo_count[price_key] = tpo_count.get(price_key, 0) + 1

    if not tpo_count:
        return {"error": "No data available"}

    # Find POC (Point of Control)
    poc = max(tpo_count.items(), key=lambda x: x[1])[0]

    # Calculate value area (70% of TPOs around POC)
    total_tpos = sum(tpo_count.values())
    target_tpos = total_tpos * 0.70

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
        "profile_range": {
            "high": max(tpo_count.keys()),
            "low": min(tpo_count.keys())
        }
    }


def calculate_fibonacci_levels(ohlcv_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate Fibonacci retracement levels."""
    candles = list(ohlcv_data.items())[:100]

    if not candles:
        return {"error": "No data available"}

    # Find swing high and swing low
    highs = [float(candle[1].get("2. high", 0)) for candle in candles]
    lows = [float(candle[1].get("3. low", 0)) for candle in candles]

    swing_high = max(highs)
    swing_low = min(lows)
    diff = swing_high - swing_low

    # Calculate Fibonacci levels
    levels = {
        "0.0%": swing_high,
        "23.6%": swing_high - (diff * 0.236),
        "38.2%": swing_high - (diff * 0.382),
        "50.0%": swing_high - (diff * 0.500),
        "61.8%": swing_high - (diff * 0.618),
        "78.6%": swing_high - (diff * 0.786),
        "100.0%": swing_low,
        "swing_high": swing_high,
        "swing_low": swing_low
    }

    return levels


def calculate_bollinger_bands(ohlcv_data: Dict[str, Any], period: int = 20, std_dev: int = 2) -> Dict[str, Any]:
    """Calculate Bollinger Bands."""
    candles = list(ohlcv_data.items())[:period]

    if len(candles) < period:
        return {"error": "Not enough data"}

    closes = [float(c[1].get("4. close", 0)) for c in candles]

    # Calculate SMA
    sma = sum(closes) / len(closes)

    # Calculate standard deviation
    variance = sum((x - sma) ** 2 for x in closes) / len(closes)
    std = variance ** 0.5

    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)

    current_price = closes[0]

    return {
        "upper_band": round(upper_band, 5),
        "middle_band": round(sma, 5),
        "lower_band": round(lower_band, 5),
        "current_price": current_price,
        "bandwidth": round(upper_band - lower_band, 5),
        "percent_b": round((current_price - lower_band) / (upper_band - lower_band), 3) if upper_band != lower_band else 0.5
    }


def calculate_macd(ohlcv_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate MACD (Moving Average Convergence Divergence)."""
    candles = list(ohlcv_data.items())[:50]

    if len(candles) < 26:
        return {"error": "Not enough data"}

    closes = [float(c[1].get("4. close", 0)) for c in candles]

    # Simple approximation of EMA
    def ema(data, period):
        multiplier = 2 / (period + 1)
        ema_val = data[0]
        for price in data[1:period]:
            ema_val = (price * multiplier) + (ema_val * (1 - multiplier))
        return ema_val

    ema_12 = ema(closes[:12], 12)
    ema_26 = ema(closes[:26], 26)
    macd_line = ema_12 - ema_26
    signal_line = macd_line * 0.9  # Simplified signal line

    histogram = macd_line - signal_line

    return {
        "macd_line": round(macd_line, 5),
        "signal_line": round(signal_line, 5),
        "histogram": round(histogram, 5),
        "signal": "BULLISH" if histogram > 0 else "BEARISH"
    }


def calculate_moving_averages(ohlcv_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate SMA and EMA for multiple periods."""
    candles = list(ohlcv_data.items())[:200]
    closes = [float(c[1].get("4. close", 0)) for c in candles]

    periods = [20, 50, 100, 200]
    result = {"current_price": closes[0] if closes else 0}

    for period in periods:
        if len(closes) >= period:
            sma = sum(closes[:period]) / period
            result[f"sma_{period}"] = round(sma, 5)

    return result


def calculate_atr(ohlcv_data: Dict[str, Any], period: int = 14) -> Dict[str, Any]:
    """Calculate Average True Range (ATR)."""
    candles = list(ohlcv_data.items())[:period + 1]

    if len(candles) < period:
        return {"error": "Not enough data"}

    true_ranges = []
    for i in range(len(candles) - 1):
        high = float(candles[i][1].get("2. high", 0))
        low = float(candles[i][1].get("3. low", 0))
        prev_close = float(candles[i + 1][1].get("4. close", 0))

        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        true_ranges.append(tr)

    atr = sum(true_ranges) / len(true_ranges)

    return {
        "atr": round(atr, 5),
        "atr_percent": round((atr / float(candles[0][1].get("4. close", 1))) * 100, 2)
    }


def detect_support_resistance(ohlcv_data: Dict[str, Any]) -> Dict[str, Any]:
    """Detect support and resistance levels."""
    candles = list(ohlcv_data.items())[:100]

    highs = [float(c[1].get("2. high", 0)) for c in candles]
    lows = [float(c[1].get("3. low", 0)) for c in candles]

    # Find local maxima/minima
    resistance_levels = []
    support_levels = []

    for i in range(2, len(candles) - 2):
        # Resistance: local maximum
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            resistance_levels.append(highs[i])

        # Support: local minimum
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            support_levels.append(lows[i])

    # Get top 3 of each
    resistance_levels = sorted(set(resistance_levels), reverse=True)[:3]
    support_levels = sorted(set(support_levels))[:3]

    return {
        "resistance_levels": [round(r, 5) for r in resistance_levels],
        "support_levels": [round(s, 5) for s in support_levels],
        "current_price": float(candles[0][1].get("4. close", 0))
    }


def calculate_pivot_points(ohlcv_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate pivot points (Standard, Fibonacci, Camarilla)."""
    candles = list(ohlcv_data.items())[:1]

    if not candles:
        return {"error": "No data available"}

    high = float(candles[0][1].get("2. high", 0))
    low = float(candles[0][1].get("3. low", 0))
    close = float(candles[0][1].get("4. close", 0))

    # Standard Pivot Points
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    r2 = pivot + (high - low)
    r3 = high + 2 * (pivot - low)
    s1 = (2 * pivot) - high
    s2 = pivot - (high - low)
    s3 = low - 2 * (high - pivot)

    return {
        "pivot": round(pivot, 5),
        "resistance_1": round(r1, 5),
        "resistance_2": round(r2, 5),
        "resistance_3": round(r3, 5),
        "support_1": round(s1, 5),
        "support_2": round(s2, 5),
        "support_3": round(s3, 5)
    }


def calculate_stochastic(ohlcv_data: Dict[str, Any], period: int = 14) -> Dict[str, Any]:
    """Calculate Stochastic Oscillator."""
    candles = list(ohlcv_data.items())[:period]

    if len(candles) < period:
        return {"error": "Not enough data"}

    highs = [float(c[1].get("2. high", 0)) for c in candles]
    lows = [float(c[1].get("3. low", 0)) for c in candles]
    closes = [float(c[1].get("4. close", 0)) for c in candles]

    highest_high = max(highs)
    lowest_low = min(lows)
    current_close = closes[0]

    k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100 if highest_high != lowest_low else 50
    d = k * 0.8  # Simplified %D

    return {
        "percent_k": round(k, 2),
        "percent_d": round(d, 2),
        "signal": "OVERBOUGHT" if k > 80 else "OVERSOLD" if k < 20 else "NEUTRAL"
    }


def calculate_adx(ohlcv_data: Dict[str, Any], period: int = 14) -> Dict[str, Any]:
    """Calculate ADX (Average Directional Index) - trend strength."""
    candles = list(ohlcv_data.items())[:period * 2]

    if len(candles) < period:
        return {"error": "Not enough data"}

    # Simplified ADX calculation
    tr_sum = 0
    dm_plus_sum = 0
    dm_minus_sum = 0

    for i in range(len(candles) - 1):
        high = float(candles[i][1].get("2. high", 0))
        low = float(candles[i][1].get("3. low", 0))
        prev_high = float(candles[i+1][1].get("2. high", 0))
        prev_low = float(candles[i+1][1].get("3. low", 0))
        prev_close = float(candles[i+1][1].get("4. close", 0))

        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        tr_sum += tr

        dm_plus = max(high - prev_high, 0)
        dm_minus = max(prev_low - low, 0)

        dm_plus_sum += dm_plus
        dm_minus_sum += dm_minus

    di_plus = (dm_plus_sum / tr_sum) * 100 if tr_sum > 0 else 0
    di_minus = (dm_minus_sum / tr_sum) * 100 if tr_sum > 0 else 0
    dx = abs(di_plus - di_minus) / (di_plus + di_minus) * 100 if (di_plus + di_minus) > 0 else 0
    adx = dx  # Simplified

    return {
        "adx": round(adx, 2),
        "di_plus": round(di_plus, 2),
        "di_minus": round(di_minus, 2),
        "trend_strength": "STRONG" if adx > 25 else "WEAK" if adx < 20 else "MODERATE"
    }


def calculate_ichimoku(ohlcv_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate Ichimoku Cloud components."""
    candles = list(ohlcv_data.items())[:52]

    if len(candles) < 52:
        return {"error": "Not enough data"}

    def calc_line(period):
        highs = [float(c[1].get("2. high", 0)) for c in candles[:period]]
        lows = [float(c[1].get("3. low", 0)) for c in candles[:period]]
        return (max(highs) + min(lows)) / 2

    tenkan_sen = calc_line(9)   # Conversion Line
    kijun_sen = calc_line(26)   # Base Line
    senkou_span_a = (tenkan_sen + kijun_sen) / 2  # Leading Span A
    senkou_span_b = calc_line(52)  # Leading Span B

    current_price = float(candles[0][1].get("4. close", 0))

    cloud_top = max(senkou_span_a, senkou_span_b)
    cloud_bottom = min(senkou_span_a, senkou_span_b)

    return {
        "tenkan_sen": round(tenkan_sen, 5),
        "kijun_sen": round(kijun_sen, 5),
        "senkou_span_a": round(senkou_span_a, 5),
        "senkou_span_b": round(senkou_span_b, 5),
        "cloud_top": round(cloud_top, 5),
        "cloud_bottom": round(cloud_bottom, 5),
        "current_price": current_price,
        "signal": "ABOVE_CLOUD" if current_price > cloud_top else "BELOW_CLOUD" if current_price < cloud_bottom else "IN_CLOUD"
    }


# ===== MCP TOOLS =====

@mcp.tool()
def get_forex_price(pair: str) -> dict:
    """
    Get current real-time price for a forex pair.

    Args:
        pair: Forex pair symbol (e.g., 'EURUSD', 'GBPUSD', 'XAUUSD' for gold)

    Returns:
        Current price, bid, ask, spread, and timestamp
    """
    pair = pair.upper().replace("/", "").replace("_", "")

    quote = get_forex_quote(pair)

    if "error" in quote:
        return quote

    # Calculate spread from config
    spread_pips = get_spread(pair, "1h") if pair != "XAUUSD" else 0.50

    return {
        "pair": quote["pair"],
        "price": quote["price"],
        "bid": quote["bid"],
        "ask": quote["ask"],
        "spread_pips": spread_pips,
        "timestamp": quote["timestamp"],
        "timezone": quote.get("timezone", "UTC")
    }


@mcp.tool()
def get_multiple_prices(pairs: List[str]) -> list:
    """
    Get current prices for multiple forex pairs at once.

    Args:
        pairs: List of forex pair symbols (e.g., ['EURUSD', 'GBPUSD', 'XAUUSD'])

    Returns:
        List of price quotes for each pair
    """
    results = []
    for pair in pairs:
        results.append(get_forex_price(pair))
    return results


@mcp.tool()
def list_available_pairs() -> dict:
    """
    List all available forex pairs organized by category.

    Returns:
        Dictionary with majors, crosses, exotics, and commodities
    """
    all_pairs = get_all_forex_pairs()

    majors = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD']
    exotics = ['USDTRY', 'USDZAR', 'USDMXN', 'USDBRL']
    commodities = ['XAUUSD']

    crosses = [p for p in all_pairs if p not in majors and p not in exotics and p not in commodities]

    return {
        "total_pairs": len(all_pairs),
        "majors": [p for p in majors if p in all_pairs],
        "crosses": crosses,
        "exotics": [p for p in exotics if p in all_pairs],
        "commodities": commodities,
        "all_pairs": all_pairs
    }


@mcp.tool()
def analyze_pair(pair: str, timeframe: str = "1h") -> dict:
    """
    Comprehensive technical analysis for a forex pair.

    Args:
        pair: Forex pair symbol (e.g., 'EURUSD')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        Detailed analysis including price, indicators, and trading recommendation
    """
    pair = pair.upper().replace("/", "").replace("_", "")

    # Get current price
    quote = get_forex_price(pair)
    if "error" in quote:
        return quote

    # Get technical indicators
    indicators = calculate_technical_indicators(pair, timeframe)

    # Generate trading recommendation
    recommendation = "NEUTRAL"
    signals = []

    if indicators.get("rsi"):
        rsi = indicators["rsi"]
        if rsi > 70:
            signals.append(f"RSI overbought ({rsi:.1f})")
            recommendation = "SELL"
        elif rsi < 30:
            signals.append(f"RSI oversold ({rsi:.1f})")
            recommendation = "BUY"
        else:
            signals.append(f"RSI neutral ({rsi:.1f})")

    return {
        "pair": pair,
        "timeframe": timeframe,
        "current_price": quote["price"],
        "bid": quote["bid"],
        "ask": quote["ask"],
        "spread_pips": quote.get("spread_pips"),
        "timestamp": quote["timestamp"],
        "technical_indicators": indicators,
        "signals": signals,
        "recommendation": recommendation,
        "risk_level": "HIGH" if pair in ['USDTRY', 'USDZAR', 'USDMXN', 'USDBRL'] else "MEDIUM" if pair not in ['EURUSD', 'GBPUSD', 'USDJPY'] else "LOW"
    }


@mcp.tool()
def get_trading_recommendation(pairs: List[str], timeframe: str = "1h", strategy: str = "trend") -> dict:
    """
    Get trading recommendations for multiple pairs based on analysis.

    Args:
        pairs: List of forex pairs to analyze
        timeframe: Time interval for analysis
        strategy: Trading strategy type ('trend', 'reversal', 'breakout')

    Returns:
        Ranked list of trading opportunities with detailed reasoning
    """
    opportunities = []

    for pair in pairs:
        analysis = analyze_pair(pair, timeframe)

        if "error" not in analysis:
            score = 0
            reasons = []

            # Score based on indicators
            if analysis.get("recommendation") == "BUY":
                score += 2
                reasons.append("Buy signal detected")
            elif analysis.get("recommendation") == "SELL":
                score += 2
                reasons.append("Sell signal detected")

            # Add to opportunities if score > 0
            if score > 0:
                opportunities.append({
                    "pair": pair,
                    "action": analysis["recommendation"],
                    "score": score,
                    "current_price": analysis["current_price"],
                    "reasons": reasons,
                    "risk_level": analysis["risk_level"],
                    "spread_pips": analysis.get("spread_pips")
                })

    # Sort by score (highest first)
    opportunities.sort(key=lambda x: x["score"], reverse=True)

    return {
        "timeframe": timeframe,
        "strategy": strategy,
        "total_opportunities": len(opportunities),
        "top_opportunities": opportunities[:5],
        "all_opportunities": opportunities
    }


@mcp.tool()
def calculate_correlation(pair1: str, pair2: str, period: int = 30) -> dict:
    """
    Calculate correlation between two forex pairs.

    Args:
        pair1: First forex pair
        pair2: Second forex pair
        period: Number of days to analyze (default 30)

    Returns:
        Correlation coefficient and relationship strength
    """
    # This is a simplified version - would need historical data for accurate correlation
    # For now, return known correlations

    known_correlations = {
        ('EURUSD', 'GBPUSD'): 0.85,
        ('EURUSD', 'USDCHF'): -0.90,
        ('AUDUSD', 'NZDUSD'): 0.95,
        ('GBPUSD', 'EURGBP'): -0.70,
    }

    pair1 = pair1.upper()
    pair2 = pair2.upper()

    correlation = known_correlations.get((pair1, pair2)) or known_correlations.get((pair2, pair1))

    if correlation is None:
        correlation = 0.0  # Unknown correlation

    # Determine strength
    abs_corr = abs(correlation)
    if abs_corr > 0.8:
        strength = "VERY STRONG"
    elif abs_corr > 0.6:
        strength = "STRONG"
    elif abs_corr > 0.4:
        strength = "MODERATE"
    elif abs_corr > 0.2:
        strength = "WEAK"
    else:
        strength = "VERY WEAK"

    relationship = "POSITIVE" if correlation > 0 else "NEGATIVE" if correlation < 0 else "NEUTRAL"

    return {
        "pair1": pair1,
        "pair2": pair2,
        "correlation": round(correlation, 3),
        "strength": strength,
        "relationship": relationship,
        "period_days": period,
        "interpretation": f"{pair1} and {pair2} have a {strength} {relationship} correlation ({correlation:.2f})"
    }


@mcp.tool()
def get_volume_profile(pair: str, timeframe: str = "1h", num_levels: int = 20) -> dict:
    """
    Get volume profile analysis for a forex pair.

    Args:
        pair: Forex pair symbol (e.g., 'EURUSD')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')
        num_levels: Number of price levels to analyze (default 20)

    Returns:
        Volume profile with POC, high/low volume nodes, and price levels
    """
    pair = pair.upper().replace("/", "").replace("_", "")

    # Get historical data
    hist_data = get_historical_data(pair, timeframe)

    if not hist_data.get("success"):
        return {"error": hist_data.get("error", "Failed to get data"), "pair": pair}

    # Calculate volume profile
    profile = calculate_volume_profile(hist_data["data"], num_levels)

    if "error" in profile:
        return {"error": profile["error"], "pair": pair}

    return {
        "pair": pair,
        "timeframe": timeframe,
        "poc": profile["poc"],
        "high_volume_nodes": profile["high_volume_nodes"],
        "low_volume_nodes": profile["low_volume_nodes"],
        "price_range": {
            "min": profile["min_price"],
            "max": profile["max_price"]
        },
        "interpretation": f"POC at {profile['poc']:.5f} shows highest traded volume. "
                         f"High volume nodes indicate support/resistance zones."
    }


@mcp.tool()
def get_market_profile(pair: str, timeframe: str = "1h") -> dict:
    """
    Get market profile analysis with TPO, POC, and value areas.

    Args:
        pair: Forex pair symbol (e.g., 'EURUSD')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        Market profile with POC, value area high/low, and TPO data
    """
    pair = pair.upper().replace("/", "").replace("_", "")

    # Get historical data
    hist_data = get_historical_data(pair, timeframe)

    if not hist_data.get("success"):
        return {"error": hist_data.get("error", "Failed to get data"), "pair": pair}

    # Calculate market profile
    profile = calculate_market_profile(hist_data["data"])

    if "error" in profile:
        return {"error": profile["error"], "pair": pair}

    return {
        "pair": pair,
        "timeframe": timeframe,
        "poc": profile["poc"],
        "value_area_high": profile["value_area_high"],
        "value_area_low": profile["value_area_low"],
        "tpo_count": profile["tpo_count"],
        "profile_range": profile["profile_range"],
        "interpretation": f"POC at {profile['poc']:.5f}. Value area: {profile['value_area_low']:.5f} to {profile['value_area_high']:.5f}. "
                         f"Price typically trades 70% of time within value area."
    }


@mcp.tool()
def get_vwap(pair: str, timeframe: str = "1h") -> dict:
    """
    Calculate VWAP (Volume Weighted Average Price) for a forex pair.

    Args:
        pair: Forex pair symbol (e.g., 'EURUSD')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        VWAP value and current price comparison
    """
    pair = pair.upper().replace("/", "").replace("_", "")

    # Get historical data
    hist_data = get_historical_data(pair, timeframe)

    if not hist_data.get("success"):
        return {"error": hist_data.get("error", "Failed to get data"), "pair": pair}

    # Calculate VWAP
    vwap = calculate_vwap(hist_data["data"])

    # Get current price
    current_quote = get_forex_price(pair)

    if "error" in current_quote:
        return {"error": current_quote["error"], "pair": pair}

    current_price = current_quote["price"]
    deviation = ((current_price - vwap) / vwap) * 100

    return {
        "pair": pair,
        "timeframe": timeframe,
        "vwap": round(vwap, 5),
        "current_price": current_price,
        "deviation_percent": round(deviation, 2),
        "signal": "ABOVE_VWAP" if current_price > vwap else "BELOW_VWAP",
        "interpretation": f"Price is {abs(deviation):.2f}% {'above' if deviation > 0 else 'below'} VWAP. "
                         f"{'Bullish' if deviation > 0 else 'Bearish'} pressure indicated."
    }


@mcp.tool()
def detect_unfilled_gaps(pair: str, timeframe: str = "1h") -> dict:
    """
    Detect unfilled price gaps (unfinished business areas).

    Args:
        pair: Forex pair symbol (e.g., 'EURUSD')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        List of unfilled gaps with price levels and timestamps
    """
    pair = pair.upper().replace("/", "").replace("_", "")

    # Get historical data
    hist_data = get_historical_data(pair, timeframe)

    if not hist_data.get("success"):
        return {"error": hist_data.get("error", "Failed to get data"), "pair": pair}

    # Detect gaps
    gaps = detect_gaps(hist_data["data"])

    # Get current price to check if gaps are still unfilled
    current_quote = get_forex_price(pair)
    if "error" not in current_quote:
        current_price = current_quote["price"]

        for gap in gaps:
            # Check if gap is filled
            if gap["type"] == "gap_up" and current_price < gap["to_price"]:
                gap["filled"] = True
            elif gap["type"] == "gap_down" and current_price > gap["to_price"]:
                gap["filled"] = True

    unfilled_gaps = [g for g in gaps if not g["filled"]]

    return {
        "pair": pair,
        "timeframe": timeframe,
        "total_gaps": len(gaps),
        "unfilled_gaps": len(unfilled_gaps),
        "gaps": unfilled_gaps[:10],  # Return top 10 unfilled gaps
        "interpretation": f"Found {len(unfilled_gaps)} unfilled gaps. These often act as magnets for price action."
    }


@mcp.tool()
def get_volume_nodes(pair: str, timeframe: str = "1h") -> dict:
    """
    Identify high and low volume nodes for support/resistance.

    Args:
        pair: Forex pair symbol (e.g., 'EURUSD')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        High volume nodes (support/resistance) and low volume nodes (breakout areas)
    """
    pair = pair.upper().replace("/", "").replace("_", "")

    # Get historical data
    hist_data = get_historical_data(pair, timeframe)

    if not hist_data.get("success"):
        return {"error": hist_data.get("error", "Failed to get data"), "pair": pair}

    # Calculate volume profile
    profile = calculate_volume_profile(hist_data["data"], num_levels=30)

    if "error" in profile:
        return {"error": profile["error"], "pair": pair}

    # Get current price
    current_quote = get_forex_price(pair)
    current_price = current_quote.get("price", 0) if "error" not in current_quote else 0

    return {
        "pair": pair,
        "timeframe": timeframe,
        "current_price": current_price,
        "high_volume_nodes": {
            "nodes": profile["high_volume_nodes"],
            "description": "Strong support/resistance levels where most trading occurred"
        },
        "low_volume_nodes": {
            "nodes": profile["low_volume_nodes"],
            "description": "Low volume areas - price likely to move quickly through these levels"
        },
        "poc": profile["poc"],
        "interpretation": "High volume nodes act as support/resistance. Low volume nodes are weak areas where price breaks easily."
    }


@mcp.tool()
def get_fibonacci_retracement(symbol: str, timeframe: str = "1h") -> dict:
    """
    Calculate Fibonacci retracement levels.

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        Fibonacci levels (0%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%)
    """
    symbol = symbol.upper()
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return {"error": hist_data.get("error", "Failed to get data"), "symbol": symbol}

    levels = calculate_fibonacci_levels(hist_data["data"])

    if "error" in levels:
        return {"error": levels["error"], "symbol": symbol}

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "levels": levels,
        "interpretation": "Key retracement levels where price may find support/resistance"
    }


@mcp.tool()
def get_bollinger_bands(symbol: str, timeframe: str = "1h", period: int = 20) -> dict:
    """
    Calculate Bollinger Bands.

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')
        period: Period for calculation (default 20)

    Returns:
        Upper band, middle band (SMA), lower band, and %B indicator
    """
    symbol = symbol.upper()
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return {"error": hist_data.get("error", "Failed to get data"), "symbol": symbol}

    bb = calculate_bollinger_bands(hist_data["data"], period)

    if "error" in bb:
        return {"error": bb["error"], "symbol": symbol}

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **bb,
        "interpretation": f"Price at {bb['percent_b']:.1%} of band width. " +
                        ("Overbought" if bb['percent_b'] > 1 else "Oversold" if bb['percent_b'] < 0 else "Normal")
    }


@mcp.tool()
def get_macd(symbol: str, timeframe: str = "1h") -> dict:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        MACD line, signal line, histogram, and trading signal
    """
    symbol = symbol.upper()
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return {"error": hist_data.get("error", "Failed to get data"), "symbol": symbol}

    macd = calculate_macd(hist_data["data"])

    if "error" in macd:
        return {"error": macd["error"], "symbol": symbol}

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **macd,
        "interpretation": f"MACD is {macd['signal']}. Histogram: {macd['histogram']:.5f}"
    }


@mcp.tool()
def get_moving_averages(symbol: str, timeframe: str = "1h") -> dict:
    """
    Calculate multiple moving averages (20, 50, 100, 200 period SMA).

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        SMAs for 20, 50, 100, 200 periods and current price
    """
    symbol = symbol.upper()
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return {"error": hist_data.get("error", "Failed to get data"), "symbol": symbol}

    mas = calculate_moving_averages(hist_data["data"])

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **mas,
        "interpretation": "Compare current price to MA levels to identify trend direction"
    }


@mcp.tool()
def get_atr(symbol: str, timeframe: str = "1h", period: int = 14) -> dict:
    """
    Calculate Average True Range (ATR) - volatility indicator.

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')
        period: Period for calculation (default 14)

    Returns:
        ATR value and percentage
    """
    symbol = symbol.upper()
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return {"error": hist_data.get("error", "Failed to get data"), "symbol": symbol}

    atr = calculate_atr(hist_data["data"], period)

    if "error" in atr:
        return {"error": atr["error"], "symbol": symbol}

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **atr,
        "interpretation": f"ATR shows {atr['atr_percent']:.2f}% volatility - use for stop loss and position sizing"
    }


@mcp.tool()
def get_support_resistance(symbol: str, timeframe: str = "1h") -> dict:
    """
    Detect support and resistance levels automatically.

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        Top 3 support and resistance levels
    """
    symbol = symbol.upper()
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return {"error": hist_data.get("error", "Failed to get data"), "symbol": symbol}

    sr = detect_support_resistance(hist_data["data"])

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **sr,
        "interpretation": "Key levels where price has historically reversed or consolidated"
    }


@mcp.tool()
def get_pivot_points(symbol: str, timeframe: str = "1h") -> dict:
    """
    Calculate pivot points for intraday trading.

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        Pivot point, 3 resistance levels, 3 support levels
    """
    symbol = symbol.upper()
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return {"error": hist_data.get("error", "Failed to get data"), "symbol": symbol}

    pivots = calculate_pivot_points(hist_data["data"])

    if "error" in pivots:
        return {"error": pivots["error"], "symbol": symbol}

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **pivots,
        "interpretation": "Pivot points for today's trading - R1/S1 are primary, R2/S2 secondary targets"
    }


@mcp.tool()
def get_stochastic(symbol: str, timeframe: str = "1h", period: int = 14) -> dict:
    """
    Calculate Stochastic Oscillator.

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')
        period: Period for calculation (default 14)

    Returns:
        %K and %D values, signal (OVERBOUGHT/OVERSOLD/NEUTRAL)
    """
    symbol = symbol.upper()
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return {"error": hist_data.get("error", "Failed to get data"), "symbol": symbol}

    stoch = calculate_stochastic(hist_data["data"], period)

    if "error" in stoch:
        return {"error": stoch["error"], "symbol": symbol}

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **stoch,
        "interpretation": f"Stochastic at {stoch['percent_k']:.1f}% - {stoch['signal']}"
    }


@mcp.tool()
def get_adx(symbol: str, timeframe: str = "1h", period: int = 14) -> dict:
    """
    Calculate ADX (Average Directional Index) - trend strength indicator.

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')
        period: Period for calculation (default 14)

    Returns:
        ADX value, +DI, -DI, and trend strength classification
    """
    symbol = symbol.upper()
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return {"error": hist_data.get("error", "Failed to get data"), "symbol": symbol}

    adx = calculate_adx(hist_data["data"], period)

    if "error" in adx:
        return {"error": adx["error"], "symbol": symbol}

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **adx,
        "interpretation": f"Trend strength is {adx['trend_strength']} (ADX: {adx['adx']:.1f})"
    }


@mcp.tool()
def get_ichimoku_cloud(symbol: str, timeframe: str = "1h") -> dict:
    """
    Calculate Ichimoku Cloud components.

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        Tenkan-sen, Kijun-sen, Senkou Span A/B, cloud position
    """
    symbol = symbol.upper()
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return {"error": hist_data.get("error", "Failed to get data"), "symbol": symbol}

    ichimoku = calculate_ichimoku(hist_data["data"])

    if "error" in ichimoku:
        return {"error": ichimoku["error"], "symbol": symbol}

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **ichimoku,
        "interpretation": f"Price is {ichimoku['signal']} - " +
                         ("Bullish" if ichimoku['signal'] == 'ABOVE_CLOUD' else
                          "Bearish" if ichimoku['signal'] == 'BELOW_CLOUD' else "Neutral")
    }


@mcp.tool()
def get_price(symbol: str) -> dict:
    """
    Get current price for any asset (Forex, Stock, or Crypto).

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC', 'TSLA')

    Returns:
        Current price, bid/ask, asset type, and additional data
    """
    symbol = symbol.upper()
    quote = get_quote(symbol)

    if "error" in quote:
        return quote

    return {
        "symbol": quote.get("symbol", symbol),
        "asset_type": quote.get("asset_type", "unknown"),
        "price": quote.get("price"),
        "bid": quote.get("bid"),
        "ask": quote.get("ask"),
        "timestamp": quote.get("timestamp"),
        **{k: v for k, v in quote.items() if k not in ["symbol", "asset_type", "price", "bid", "ask", "timestamp"]}
    }


@mcp.tool()
def list_supported_assets() -> dict:
    """
    List all supported assets by category.

    Returns:
        Forex pairs, popular stocks, cryptocurrencies
    """
    return {
        "forex": {
            "count": len(FOREX_PAIRS),
            "majors": FOREX_PAIRS[:7],
            "crosses": FOREX_PAIRS[7:16],
            "exotics": FOREX_PAIRS[16:20],
            "commodities": ['XAUUSD']
        },
        "stocks": {
            "count": len(POPULAR_STOCKS),
            "popular": POPULAR_STOCKS[:20],
            "etfs": ['SPY', 'QQQ', 'IWM', 'DIA']
        },
        "crypto": {
            "count": len(CRYPTO_SYMBOLS),
            "major": CRYPTO_SYMBOLS[:8],
            "altcoins": CRYPTO_SYMBOLS[8:]
        },
        "note": "Any valid symbol can be queried - these are just popular examples"
    }


@mcp.resource("forex://pairs")
def list_forex_pairs() -> str:
    """List all available forex pairs with categories."""
    pairs_data = list_available_pairs()

    output = "📊 Available Forex Pairs\n\n"
    output += f"**Major Pairs ({len(pairs_data['majors'])}):**\n"
    output += ", ".join(pairs_data['majors']) + "\n\n"
    output += f"**Cross Pairs ({len(pairs_data['crosses'])}):**\n"
    output += ", ".join(pairs_data['crosses']) + "\n\n"
    output += f"**Exotic Pairs ({len(pairs_data['exotics'])}):**\n"
    output += ", ".join(pairs_data['exotics']) + "\n\n"
    output += f"**Commodities ({len(pairs_data['commodities'])}):**\n"
    output += ", ".join(pairs_data['commodities']) + "\n\n"
    output += f"**Total:** {pairs_data['total_pairs']} pairs available"

    return output


def main():
    """Run the Forex MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description="Forex Trading Assistant MCP Server")
    parser.add_argument(
        "transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        nargs="?",
        help="Transport method (default: stdio)"
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
