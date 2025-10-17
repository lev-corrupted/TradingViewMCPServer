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

import logging
import sys
from pathlib import Path
from typing import Dict, List, Any

# Setup logging
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(log_dir / 'tradingview_mcp.log')
    ]
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Import our refactored modules
from tradingview_mcp.api import AlphaVantageClient
from tradingview_mcp.config import (
    FOREX_PAIRS,
    POPULAR_STOCKS,
    CRYPTO_SYMBOLS,
    TYPICAL_SPREADS,
    DEFAULT_SPREAD,
    HIGH_RISK_PAIRS,
    MAJOR_PAIRS,
    KNOWN_CORRELATIONS,
)
from tradingview_mcp.utils import (
    detect_asset_type,
    format_error_response,
    format_success_response,
    validate_api_key,
)
from tradingview_mcp.indicators import (
    calculate_moving_averages,
    calculate_macd,
    calculate_adx,
    calculate_ichimoku,
    calculate_stochastic,
    calculate_fibonacci_levels,
    calculate_rsi,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_vwap,
    calculate_volume_profile,
    calculate_market_profile,
    detect_support_resistance,
    calculate_pivot_points,
    detect_gaps,
)

# Import Pine Script modules
from tradingview_mcp.pine_script import (
    PineScriptValidator,
    PineDocumentation,
    PineSandbox,
    ErrorExplainer,
    VersionDetector,
    VersionConverter,
    PineAutocomplete,
)

# Validate environment setup
import os
api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
if api_key:
    is_valid, error_msg = validate_api_key(api_key)
    if not is_valid:
        logger.warning(f"API key validation warning: {error_msg}")
else:
    logger.error("ALPHA_VANTAGE_API_KEY not set. Server will not function properly.")

# Initialize API client
api_client = AlphaVantageClient()

# Initialize Pine Script components
pine_validator = PineScriptValidator()
pine_docs = PineDocumentation()
pine_sandbox = PineSandbox()
pine_errors = ErrorExplainer()
pine_version_detector = VersionDetector()
pine_version_converter = VersionConverter()
pine_autocomplete = PineAutocomplete()

# Initialize MCP server
mcp = FastMCP(
    name="TradingView Multi-Asset Trading Assistant",
    instructions=(
        "Professional trading assistant providing real-time market data, "
        "technical analysis, and trading recommendations for multiple asset classes. "
        "Supports Forex (22+ pairs), Stocks (US equities), and Crypto (BTC, ETH, etc). "
        "Includes advanced tools: Volume Profile, Market Profile, VWAP, Fibonacci, "
        "Bollinger Bands, MACD, Moving Averages, ATR, Support/Resistance, Pivot Points, "
        "Stochastic, ADX, Ichimoku Cloud, and more. "
        "\n\n"
        "PINE SCRIPT SUPPORT: Comprehensive Pine Script development tools including "
        "real-time syntax validation, function documentation, code testing sandbox, "
        "error explanations, version detection (v1-v6), version conversion, and "
        "intelligent autocomplete. Full support for Pine Script v6 with type, enum, and map!"
    ),
)

logger.info("TradingView MCP Server initialized")


# ===== HELPER FUNCTIONS =====

def get_quote(symbol: str) -> Dict[str, Any]:
    """
    Universal quote fetcher for all asset types.

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')

    Returns:
        Quote data or error
    """
    asset_type, formatted_symbol = detect_asset_type(symbol)

    logger.info(f"Fetching quote for {symbol} (type: {asset_type})")

    if asset_type == 'forex':
        return api_client.get_forex_quote(formatted_symbol)
    elif asset_type == 'crypto':
        return api_client.get_crypto_quote(formatted_symbol)
    else:  # stock
        return api_client.get_stock_quote(formatted_symbol)


def get_historical_data(
    symbol: str,
    timeframe: str = "1h",
    outputsize: str = "compact"
) -> Dict[str, Any]:
    """
    Get historical data for any asset type.

    Args:
        symbol: Symbol to fetch
        timeframe: Timeframe (5m, 15m, 30m, 1h, 4h, 1d)
        outputsize: 'compact' or 'full'

    Returns:
        Historical OHLCV data or error
    """
    asset_type, formatted_symbol = detect_asset_type(symbol)

    logger.info(f"Fetching historical data for {symbol} ({timeframe})")

    # Currently only forex is fully implemented in API client
    # TODO: Extend API client for stocks and crypto historical data
    if asset_type == 'forex':
        return api_client.get_historical_data_forex(formatted_symbol, timeframe, outputsize)
    else:
        return format_error_response(
            f"Historical data for {asset_type} not yet fully implemented",
            symbol=symbol,
            suggestion="Use forex pairs for now, or wait for update"
        )


def get_spread(pair: str) -> float:
    """Get typical spread for a pair."""
    return TYPICAL_SPREADS.get(pair, DEFAULT_SPREAD)


# ===== MCP TOOLS: MARKET DATA =====

@mcp.tool()
def get_price(symbol: str) -> dict:
    """
    Get current price for any asset (Forex, Stock, or Crypto).

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC', 'TSLA')

    Returns:
        Current price, bid/ask, asset type, and additional data
    """
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
        **{k: v for k, v in quote.items()
           if k not in ["symbol", "asset_type", "price", "bid", "ask", "timestamp"]}
    }


@mcp.tool()
def get_multiple_prices(symbols: List[str]) -> list:
    """
    Get current prices for multiple symbols at once.

    Args:
        symbols: List of symbols (e.g., ['EURUSD', 'AAPL', 'BTC'])

    Returns:
        List of price quotes for each symbol
    """
    results = []
    for symbol in symbols:
        results.append(get_price(symbol))
    return results


@mcp.tool()
def list_available_pairs() -> dict:
    """
    List all available forex pairs organized by category.

    Returns:
        Dictionary with majors, crosses, exotics, and commodities
    """
    majors = [p for p in MAJOR_PAIRS if p in FOREX_PAIRS]
    exotics = ['USDTRY', 'USDZAR', 'USDMXN', 'USDBRL']
    commodities = ['XAUUSD']
    crosses = [p for p in FOREX_PAIRS
               if p not in majors and p not in exotics and p not in commodities]

    return {
        "total_pairs": len(FOREX_PAIRS),
        "majors": majors,
        "crosses": crosses,
        "exotics": exotics,
        "commodities": commodities,
        "all_pairs": FOREX_PAIRS
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


# ===== MCP TOOLS: TECHNICAL ANALYSIS =====

@mcp.tool()
def analyze_pair(symbol: str, timeframe: str = "1h") -> dict:
    """
    Comprehensive technical analysis for any symbol.

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        Detailed analysis including price, indicators, and trading recommendation
    """
    # Get current price
    quote = get_quote(symbol)
    if "error" in quote:
        return quote

    asset_type = quote.get("asset_type", "unknown")

    # Get historical data for analysis
    hist_data = get_historical_data(symbol, timeframe)
    if not hist_data.get("success"):
        # Return basic quote if can't get historical data
        return {
            "symbol": symbol,
            "asset_type": asset_type,
            "timeframe": timeframe,
            "current_price": quote["price"],
            "bid": quote["bid"],
            "ask": quote["ask"],
            "timestamp": quote["timestamp"],
            "note": "Limited analysis - historical data unavailable"
        }

    # Calculate indicators
    ma = calculate_moving_averages(hist_data["data"])
    bb = calculate_bollinger_bands(hist_data["data"])

    # Generate signals and recommendation
    signals = []
    recommendation = "NEUTRAL"

    # Analyze Bollinger Bands
    if "percent_b" in bb:
        if bb["percent_b"] > 1:
            signals.append("Price above upper Bollinger Band (overbought)")
            recommendation = "SELL"
        elif bb["percent_b"] < 0:
            signals.append("Price below lower Bollinger Band (oversold)")
            recommendation = "BUY"

    # Risk classification
    if asset_type == 'forex' and symbol in HIGH_RISK_PAIRS:
        risk_level = "HIGH"
    elif asset_type == 'forex' and symbol in MAJOR_PAIRS:
        risk_level = "LOW"
    else:
        risk_level = "MEDIUM"

    return {
        "symbol": symbol,
        "asset_type": asset_type,
        "timeframe": timeframe,
        "current_price": quote["price"],
        "bid": quote["bid"],
        "ask": quote["ask"],
        "timestamp": quote["timestamp"],
        "moving_averages": ma,
        "bollinger_bands": bb,
        "signals": signals,
        "recommendation": recommendation,
        "risk_level": risk_level
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
    pair1 = pair1.upper().replace("/", "").replace("_", "")
    pair2 = pair2.upper().replace("/", "").replace("_", "")

    # Check known correlations
    correlation = (KNOWN_CORRELATIONS.get((pair1, pair2)) or
                   KNOWN_CORRELATIONS.get((pair2, pair1)))

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


# ===== MCP TOOLS: FIBONACCI & PIVOT POINTS =====

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
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return hist_data

    levels = calculate_fibonacci_levels(hist_data["data"])

    if "error" in levels:
        return levels

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "levels": levels,
        "interpretation": "Key retracement levels where price may find support/resistance"
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
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return hist_data

    pivots = calculate_pivot_points(hist_data["data"])

    if "error" in pivots:
        return pivots

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **pivots
    }


# ===== MCP TOOLS: TREND INDICATORS =====

@mcp.tool()
def get_moving_averages(symbol: str, timeframe: str = "1h") -> dict:
    """
    Calculate multiple moving averages (20, 50, 100, 200 period SMA/EMA).

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        SMAs and EMAs for 20, 50, 100, 200 periods and current price
    """
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return hist_data

    mas = calculate_moving_averages(hist_data["data"])

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **mas,
        "interpretation": "Compare current price to MA levels to identify trend direction"
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
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return hist_data

    macd = calculate_macd(hist_data["data"])

    if "error" in macd:
        return macd

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **macd,
        "interpretation": f"MACD is {macd['signal']}. Histogram: {macd['histogram']:.5f}"
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
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return hist_data

    adx = calculate_adx(hist_data["data"], period)

    if "error" in adx:
        return adx

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
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return hist_data

    ichimoku = calculate_ichimoku(hist_data["data"])

    if "error" in ichimoku:
        return ichimoku

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **ichimoku
    }


# ===== MCP TOOLS: MOMENTUM INDICATORS =====

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
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return hist_data

    stoch = calculate_stochastic(hist_data["data"], period)

    if "error" in stoch:
        return stoch

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **stoch
    }


@mcp.tool()
def get_rsi(symbol: str, timeframe: str = "1h", period: int = 14) -> dict:
    """
    Calculate RSI (Relative Strength Index).

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')
        period: Period for calculation (default 14)

    Returns:
        RSI value and signal (OVERBOUGHT/OVERSOLD/NEUTRAL)
    """
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return hist_data

    rsi = calculate_rsi(hist_data["data"], period)

    if "error" in rsi:
        return rsi

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **rsi
    }


# ===== MCP TOOLS: VOLATILITY INDICATORS =====

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
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return hist_data

    bb = calculate_bollinger_bands(hist_data["data"], period)

    if "error" in bb:
        return bb

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **bb
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
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return hist_data

    atr = calculate_atr(hist_data["data"], period)

    if "error" in atr:
        return atr

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **atr
    }


# ===== MCP TOOLS: VOLUME INDICATORS =====

@mcp.tool()
def get_vwap(symbol: str, timeframe: str = "1h") -> dict:
    """
    Calculate VWAP (Volume Weighted Average Price).

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        VWAP value and current price comparison
    """
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return hist_data

    vwap = calculate_vwap(hist_data["data"])

    # Get current price
    current_quote = get_quote(symbol)
    if "error" in current_quote:
        return current_quote

    current_price = current_quote["price"]
    deviation = ((current_price - vwap) / vwap) * 100 if vwap > 0 else 0

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "vwap": round(vwap, 5),
        "current_price": current_price,
        "deviation_percent": round(deviation, 2),
        "signal": "ABOVE_VWAP" if current_price > vwap else "BELOW_VWAP",
        "interpretation": f"Price is {abs(deviation):.2f}% {'above' if deviation > 0 else 'below'} VWAP. "
                         f"{'Bullish' if deviation > 0 else 'Bearish'} pressure indicated."
    }


@mcp.tool()
def get_volume_profile(symbol: str, timeframe: str = "1h", num_levels: int = 20) -> dict:
    """
    Get volume profile analysis.

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')
        num_levels: Number of price levels to analyze (default 20)

    Returns:
        Volume profile with POC, high/low volume nodes, and price levels
    """
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return hist_data

    profile = calculate_volume_profile(hist_data["data"], num_levels)

    if "error" in profile:
        return profile

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **profile,
        "interpretation": f"POC at {profile['poc']:.5f} shows highest traded volume. "
                         f"High volume nodes indicate support/resistance zones."
    }


@mcp.tool()
def get_market_profile(symbol: str, timeframe: str = "1h") -> dict:
    """
    Get market profile analysis with TPO, POC, and value areas.

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        Market profile with POC, value area high/low, and TPO data
    """
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return hist_data

    profile = calculate_market_profile(hist_data["data"])

    if "error" in profile:
        return profile

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **profile
    }


# ===== MCP TOOLS: SUPPORT/RESISTANCE =====

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
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return hist_data

    sr = detect_support_resistance(hist_data["data"])

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        **sr
    }


@mcp.tool()
def detect_unfilled_gaps(symbol: str, timeframe: str = "1h") -> dict:
    """
    Detect unfilled price gaps (unfinished business areas).

    Args:
        symbol: Symbol (e.g., 'EURUSD', 'AAPL', 'BTC')
        timeframe: Time interval ('5m', '15m', '1h', '4h', '1d')

    Returns:
        List of unfilled gaps with price levels and timestamps
    """
    hist_data = get_historical_data(symbol, timeframe)

    if not hist_data.get("success"):
        return hist_data

    gaps = detect_gaps(hist_data["data"])

    # Get current price to check if gaps are still unfilled
    current_quote = get_quote(symbol)
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
        "symbol": symbol,
        "timeframe": timeframe,
        "total_gaps": len(gaps),
        "unfilled_gaps": len(unfilled_gaps),
        "gaps": unfilled_gaps[:10],  # Return top 10
        "interpretation": f"Found {len(unfilled_gaps)} unfilled gaps. These often act as magnets for price action."
    }


# ===== MCP TOOLS: SYSTEM =====

@mcp.tool()
def get_server_stats() -> dict:
    """
    Get server statistics including API usage and cache performance.

    Returns:
        Server statistics
    """
    return {
        "status": "online",
        **api_client.get_stats()
    }


# ===== MCP RESOURCES =====

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


# ===== PINE SCRIPT MCP TOOLS =====

@mcp.tool()
def validate_pine_script(code: str, version: int = None) -> dict:
    """
    Validate Pine Script code for syntax and semantic errors.

    Checks for:
    - Syntax errors (missing brackets, invalid operators, etc.)
    - Function signature errors (wrong parameters, unknown functions)
    - Deprecated function usage
    - Version compatibility issues
    - Type errors

    Args:
        code: Pine Script source code to validate
        version: Target Pine Script version (1-6). Auto-detected if not provided.

    Returns:
        Validation result with errors, warnings, and suggestions

    Example:
        validate_pine_script("//@version=5\\nindicator(\\"Test\\")\\nplot(ta.sma(close, 20))")
    """
    try:
        result = pine_validator.validate(code, version)

        return {
            "valid": result.valid,
            "version": result.version,
            "errors": [
                {
                    "line": err.line,
                    "column": err.column,
                    "severity": err.severity,
                    "message": err.message,
                    "code": err.code,
                    "suggestion": err.suggestion,
                }
                for err in result.errors
            ],
            "warnings": [
                {
                    "line": warn.line,
                    "column": warn.column,
                    "message": warn.message,
                    "suggestion": warn.suggestion,
                }
                for warn in result.warnings
            ],
            "info": [
                {
                    "message": info.message,
                }
                for info in result.info
            ],
            "summary": f"Validation {'passed' if result.valid else 'failed'} - "
                       f"{len(result.errors)} errors, {len(result.warnings)} warnings",
        }
    except Exception as e:
        logger.error(f"Pine Script validation error: {e}")
        return format_error_response(str(e), suggestion="Check code syntax")


@mcp.tool()
def get_pine_documentation(function_name: str, version: int = 5) -> dict:
    """
    Get comprehensive documentation for a Pine Script function or topic.

    Provides:
    - Function signature and parameters
    - Return type
    - Description and usage
    - Code examples
    - Related functions
    - Links to official documentation

    Args:
        function_name: Function name (e.g., 'ta.sma', 'plot', 'indicator', 'map.new') or topic
        version: Pine Script version (default: 5, v6 supported)

    Returns:
        Detailed documentation with examples

    Example:
        get_pine_documentation("ta.sma")
    """
    try:
        # Try function documentation first
        docs = pine_docs.get_function_docs(function_name, version)

        if docs:
            return {
                "function": function_name,
                "version": version,
                "documentation": docs,
                "type": "function",
            }

        # Try topic documentation
        topic_docs = pine_docs.get_topic_docs(function_name)
        if topic_docs:
            return {
                "topic": function_name,
                "version": version,
                "documentation": topic_docs,
                "type": "topic",
            }

        # Search for similar functions
        search_results = pine_docs.search(function_name, version)
        if search_results:
            return {
                "query": function_name,
                "message": f"Function '{function_name}' not found. Did you mean:",
                "suggestions": search_results[:5],
                "type": "search_results",
            }

        return format_error_response(
            f"Documentation for '{function_name}' not found",
            suggestion="Check function name spelling or try searching"
        )

    except Exception as e:
        logger.error(f"Pine documentation error: {e}")
        return format_error_response(str(e))


@mcp.tool()
def test_pine_script(
    code: str,
    symbol: str = "BTCUSD",
    timeframe: str = "1D",
    bars: int = 100,
) -> dict:
    """
    Test Pine Script code in a safe sandbox environment.

    Validates syntax, simulates execution, and provides performance metrics.
    Note: Full backtesting requires TradingView platform integration.

    Args:
        code: Pine Script code to test
        symbol: Symbol to test with (default: BTCUSD)
        timeframe: Timeframe (default: 1D)
        bars: Number of bars to simulate (default: 100)

    Returns:
        Test results with validation, metrics, and any errors

    Example:
        test_pine_script("//@version=5\\nindicator(\\"Test\\")\\nplot(close)", "AAPL", "1h")
    """
    try:
        result = pine_sandbox.test(code, symbol, timeframe, bars)

        return {
            "success": result.success,
            "validation_passed": result.validation_passed,
            "output": result.output,
            "errors": result.errors,
            "warnings": result.warnings,
            "execution_time_ms": round(result.execution_time * 1000, 2),
            "metrics": result.metrics,
            "symbol": symbol,
            "timeframe": timeframe,
        }

    except Exception as e:
        logger.error(f"Pine sandbox error: {e}")
        return format_error_response(str(e), suggestion="Check code syntax")


@mcp.tool()
def explain_pine_error(error_code: str, error_message: str = "") -> dict:
    """
    Get detailed explanation for a Pine Script error.

    Provides:
    - Error description
    - Common causes
    - Multiple solutions
    - Code examples showing correct usage
    - Links to documentation

    Args:
        error_code: Error code (e.g., 'E001', 'E101')
        error_message: Original error message (optional)

    Returns:
        Comprehensive error explanation with solutions

    Example:
        explain_pine_error("E101", "Unknown function: sma")
    """
    try:
        explanation = pine_errors.explain(error_code, error_message)

        return {
            "error_code": explanation.error_code,
            "title": explanation.title,
            "description": explanation.description,
            "causes": explanation.causes,
            "solutions": explanation.solutions,
            "examples": explanation.examples,
            "documentation": explanation.related_docs,
            "formatted": pine_errors.format_explanation(explanation),
        }

    except Exception as e:
        logger.error(f"Pine error explanation error: {e}")
        return format_error_response(str(e))


@mcp.tool()
def detect_pine_version(code: str) -> dict:
    """
    Detect Pine Script version from code and analyze compatibility.

    Analyzes:
    - Version directive (//@version=5)
    - Syntax features (v5 namespaces, v4 var keyword, etc.)
    - Function usage patterns
    - Deprecated features
    - Compatibility issues

    Args:
        code: Pine Script code to analyze

    Returns:
        Detected version, confidence, issues, and upgrade suggestions

    Example:
        detect_pine_version("study(\\"Test\\")\\nmyMa = sma(close, 20)")
    """
    try:
        version_info = pine_version_detector.detect_version(code)

        return {
            "detected_version": version_info.version,
            "detection_source": version_info.detected_from,
            "confidence": f"{version_info.confidence:.0%}",
            "compatibility_issues": version_info.compatibility_issues,
            "deprecated_features": version_info.deprecated_features,
            "suggestions": version_info.suggestions,
            "summary": f"Detected Pine Script v{version_info.version} "
                       f"(confidence: {version_info.confidence:.0%}, from: {version_info.detected_from})",
        }

    except Exception as e:
        logger.error(f"Pine version detection error: {e}")
        return format_error_response(str(e))


@mcp.tool()
def convert_pine_version(code: str, target_version: int, source_version: int = None) -> dict:
    """
    Convert Pine Script code between versions.

    Automatically converts:
    - Function names (sma -> ta.sma in v5)
    - study() -> indicator()
    - security() -> request.security()
    - Namespace additions (ta., math., str.)

    Supports:
    - v3 -> v4 conversion
    - v4 -> v5 conversion
    - Automatic source version detection

    Args:
        code: Source Pine Script code
        target_version: Target version (1-6)
        source_version: Source version (auto-detected if not provided)

    Returns:
        Converted code, list of changes, and warnings

    Example:
        convert_pine_version("study(\\"Test\\")\\nplot(sma(close, 20))", 5)
    """
    try:
        converted_code, changes, warnings = pine_version_converter.convert(
            code, target_version, source_version
        )

        return {
            "success": True,
            "source_version": source_version or "auto-detected",
            "target_version": target_version,
            "converted_code": converted_code,
            "changes_made": changes,
            "warnings": warnings,
            "summary": f"Converted from v{source_version or '?'} to v{target_version} - "
                       f"{len(changes)} changes made",
        }

    except Exception as e:
        logger.error(f"Pine version conversion error: {e}")
        return format_error_response(str(e), suggestion="Check source code syntax")


@mcp.tool()
def autocomplete_pine(code: str, cursor_position: int) -> dict:
    """
    Get intelligent autocomplete suggestions for Pine Script code.

    Provides:
    - Function completions with signatures
    - Parameter hints
    - Keyword completions
    - Built-in variable suggestions
    - Context-aware namespace completions (ta., math., str.)

    Args:
        code: Current Pine Script code
        cursor_position: Character position of cursor in code

    Returns:
        List of autocomplete suggestions with documentation

    Example:
        autocomplete_pine("indicator(\\"Test\\")\\nta.", 25)
    """
    try:
        suggestions = pine_autocomplete.get_completions(code, cursor_position)

        return {
            "suggestions": [
                {
                    "label": item.label,
                    "kind": item.kind,
                    "detail": item.detail,
                    "documentation": item.documentation,
                    "insert_text": item.insert_text,
                }
                for item in suggestions
            ],
            "count": len(suggestions),
            "cursor_position": cursor_position,
        }

    except Exception as e:
        logger.error(f"Pine autocomplete error: {e}")
        return format_error_response(str(e))


@mcp.tool()
def get_pine_template(template_type: str = "simple") -> dict:
    """
    Get Pine Script code templates for common indicator types.

    Available templates:
    - simple: Basic indicator with moving average
    - strategy: Trading strategy with entries/exits
    - overlay: Support/resistance overlay indicator

    Args:
        template_type: Template type ('simple', 'strategy', 'overlay')

    Returns:
        Ready-to-use Pine Script template code

    Example:
        get_pine_template("strategy")
    """
    try:
        template = pine_sandbox.get_test_template(template_type)

        return {
            "template_type": template_type,
            "code": template,
            "description": f"Pine Script {template_type} indicator template",
        }

    except Exception as e:
        logger.error(f"Pine template error: {e}")
        return format_error_response(
            str(e),
            suggestion="Use 'simple', 'strategy', or 'overlay'"
        )


# ===== MAIN =====

def main():
    """Run the TradingView MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description="TradingView Trading Assistant MCP Server")
    parser.add_argument(
        "transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        nargs="?",
        help="Transport method (default: stdio)"
    )
    args = parser.parse_args()

    logger.info(f"Starting server with transport: {args.transport}")

    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
