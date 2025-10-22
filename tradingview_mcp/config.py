"""
Configuration and constants for TradingView MCP Server.
"""

from typing import Dict

# ==== API Configuration ====
API_REQUEST_TIMEOUT = 10  # seconds
CACHE_TTL_QUOTES = 300  # 5 minutes for price quotes
CACHE_TTL_HISTORICAL = 900  # 15 minutes for historical data
RATE_LIMIT_CALLS_PER_MINUTE = 5  # Alpha Vantage free tier limit
RATE_LIMIT_CALLS_PER_DAY = 25  # Alpha Vantage free tier daily limit

# ==== Asset Lists ====
FOREX_PAIRS = [
    # Majors
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "USDCHF",
    "AUDUSD",
    "USDCAD",
    "NZDUSD",
    # Crosses
    "GBPJPY",
    "EURJPY",
    "AUDJPY",
    "NZDJPY",
    "EURGBP",
    "EURAUD",
    "EURCHF",
    "GBPAUD",
    "GBPCAD",
    "AUDCAD",
    # Exotics
    "USDTRY",
    "USDZAR",
    "USDMXN",
    "USDBRL",
    # Commodities
    "XAUUSD",
]

POPULAR_STOCKS = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "TSLA",
    "NVDA",
    "META",
    "BRK.B",
    "V",
    "JPM",
    "JNJ",
    "WMT",
    "PG",
    "MA",
    "DIS",
    "HD",
    "BAC",
    "NFLX",
    "CSCO",
    "ADBE",
    "CRM",
    "INTC",
    "AMD",
    "PYPL",
    "NKE",
    "ORCL",
    "SPY",
    "QQQ",
    "IWM",
    "DIA",  # ETFs
]

CRYPTO_SYMBOLS = [
    "BTC",
    "ETH",
    "BNB",
    "XRP",
    "ADA",
    "DOGE",
    "SOL",
    "MATIC",
    "DOT",
    "AVAX",
    "LINK",
    "UNI",
    "LTC",
    "ATOM",
    "XLM",
    "ALGO",
]

# ==== Typical Spreads (pips) ====
TYPICAL_SPREADS: Dict[str, float] = {
    "EURUSD": 1.5,
    "GBPUSD": 2.0,
    "USDJPY": 1.5,
    "USDCHF": 2.0,
    "AUDUSD": 2.0,
    "USDCAD": 2.5,
    "NZDUSD": 3.0,
    "GBPJPY": 5.0,
    "EURJPY": 3.0,
    "AUDJPY": 4.0,
    "NZDJPY": 5.0,
    "EURGBP": 2.5,
    "EURAUD": 4.0,
    "EURCHF": 3.0,
    "GBPAUD": 6.0,
    "GBPCAD": 5.0,
    "AUDCAD": 4.0,
    "USDTRY": 30.0,
    "USDZAR": 50.0,
    "USDMXN": 40.0,
    "USDBRL": 60.0,
    "XAUUSD": 0.50,
}
DEFAULT_SPREAD = 3.0

# ==== Technical Indicator Parameters ====

# Crypto spread approximation (when exact bid/ask not available)
CRYPTO_SPREAD_MULTIPLIER_BID = 0.999  # 0.1% below mid price
CRYPTO_SPREAD_MULTIPLIER_ASK = 1.001  # 0.1% above mid price

# MACD parameters
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9
MACD_SIGNAL_SMOOTHING = 0.9  # Simplified signal line multiplier

# Stochastic parameters
STOCHASTIC_K_PERIOD = 14
STOCHASTIC_D_PERIOD = 3
STOCHASTIC_D_SMOOTHING = 0.8  # Simplified %D multiplier
STOCHASTIC_OVERBOUGHT = 80
STOCHASTIC_OVERSOLD = 20

# ADX parameters
ADX_PERIOD = 14
ADX_STRONG_TREND = 25
ADX_WEAK_TREND = 20

# Bollinger Bands parameters
BB_PERIOD = 20
BB_STD_DEV = 2

# ATR parameters
ATR_PERIOD = 14

# Moving Average periods
MA_PERIODS = [20, 50, 100, 200]

# Ichimoku parameters
ICHIMOKU_TENKAN_PERIOD = 9  # Conversion Line
ICHIMOKU_KIJUN_PERIOD = 26  # Base Line
ICHIMOKU_SENKOU_B_PERIOD = 52  # Leading Span B

# RSI parameters
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# Volume Profile parameters
VOLUME_PROFILE_LEVELS = 20
VOLUME_PROFILE_VALUE_AREA = 0.70  # 70% of volume

# ==== Timeframe Mapping ====
TIMEFRAME_MAP = {
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "1h": "60min",
    "4h": "daily",  # Alpha Vantage limitation
    "1d": "daily",
}

# ==== Risk Classifications ====
HIGH_RISK_PAIRS = ["USDTRY", "USDZAR", "USDMXN", "USDBRL"]
MAJOR_PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]

# ==== Known Correlations ====
# Correlation coefficient between -1 and 1
KNOWN_CORRELATIONS: Dict[tuple[str, str], float] = {
    ("EURUSD", "GBPUSD"): 0.85,
    ("EURUSD", "USDCHF"): -0.90,
    ("AUDUSD", "NZDUSD"): 0.95,
    ("GBPUSD", "EURGBP"): -0.70,
    ("EURUSD", "USDJPY"): -0.65,
    ("GBPUSD", "USDJPY"): -0.60,
    ("AUDUSD", "XAUUSD"): 0.75,
}

# ==== Data Limits ====
MAX_HISTORICAL_CANDLES = 200
RECENT_CANDLES_FOR_ANALYSIS = 100
GAPS_DETECTION_CANDLES = 50
MARKET_PROFILE_CANDLES = 30

# ==== Fibonacci Levels ====
FIBONACCI_LEVELS = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]

# ==== Error Messages ====
ERROR_RATE_LIMIT = "API rate limit reached. Please wait a minute and try again."
ERROR_NO_DATA = "No data available for the requested symbol."
ERROR_INVALID_SYMBOL = "Invalid symbol provided."
ERROR_API_KEY_MISSING = "ALPHA_VANTAGE_API_KEY not found in environment variables."
ERROR_NETWORK = "Network error while fetching data. Please check your connection."
ERROR_INSUFFICIENT_DATA = "Insufficient historical data for this calculation."
