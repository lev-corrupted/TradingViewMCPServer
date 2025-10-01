from __future__ import annotations
import os
from typing import Set

ALLOWED_TIMEFRAMES: Set[str] = {"5m", "15m", "1h", "4h", "1D", "1W", "1M"}
EXCHANGE_SCREENER = {
    "all": "crypto",
    "huobi": "crypto",
    "kucoin": "crypto",
    "coinbase": "crypto",
    "gateio": "crypto",
    "binance": "crypto",
    "bitfinex": "crypto",
    "bybit": "crypto",
    "okx": "crypto",
    "bist": "turkey",
    "nasdaq": "america",
}

# Get absolute path to coinlist directory relative to this module
# This file is at: src/tradingview_mcp/core/utils/validators.py
# We want: src/tradingview_mcp/coinlist/
_this_file = __file__
_utils_dir = os.path.dirname(_this_file)  # core/utils
_core_dir = os.path.dirname(_utils_dir)   # core  
_package_dir = os.path.dirname(_core_dir) # tradingview_mcp
COINLIST_DIR = os.path.join(_package_dir, 'coinlist')


def sanitize_timeframe(tf: str, default: str = "5m") -> str:
    if not tf:
        return default
    tfs = tf.strip()
    return tfs if tfs in ALLOWED_TIMEFRAMES else default


def sanitize_exchange(ex: str, default: str = "kucoin") -> str:
    if not ex:
        return default
    exs = ex.strip().lower()
    return exs if exs in EXCHANGE_SCREENER else default
