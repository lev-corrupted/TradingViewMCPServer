"""Alpha Vantage API client with rate limiting and caching."""

import os
import time
import logging
from typing import Dict, Any, Optional
from collections import deque
from datetime import datetime

import requests

from ..config import (
    API_REQUEST_TIMEOUT,
    CACHE_TTL_QUOTES,
    CACHE_TTL_HISTORICAL,
    RATE_LIMIT_CALLS_PER_MINUTE,
    TIMEFRAME_MAP,
    ERROR_RATE_LIMIT,
    ERROR_NO_DATA,
    ERROR_API_KEY_MISSING,
    ERROR_NETWORK,
)
from ..utils.formatters import format_error_response, safe_float
from ..utils.asset_detector import format_pair_for_alpha_vantage
from .cache import ResponseCache

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter using sliding window."""

    def __init__(self, max_calls: int, time_window: int):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: deque = deque()

    def can_proceed(self) -> bool:
        """Check if a call can proceed without hitting rate limit."""
        now = time.time()
        # Remove calls outside the time window
        while self.calls and self.calls[0] < now - self.time_window:
            self.calls.popleft()

        return len(self.calls) < self.max_calls

    def record_call(self) -> None:
        """Record a new API call."""
        self.calls.append(time.time())

    def wait_time(self) -> float:
        """Get seconds to wait before next call."""
        if not self.calls:
            return 0

        now = time.time()
        # Remove calls outside the time window
        while self.calls and self.calls[0] < now - self.time_window:
            self.calls.popleft()

        if len(self.calls) < self.max_calls:
            return 0

        # Wait until oldest call expires
        oldest_call = self.calls[0]
        wait_seconds = (oldest_call + self.time_window) - now
        return max(0, wait_seconds)


class AlphaVantageClient:
    """
    Alpha Vantage API client with caching and rate limiting.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Alpha Vantage client.

        Args:
            api_key: Alpha Vantage API key (or from env)
        """
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            logger.error(ERROR_API_KEY_MISSING)

        self.base_url = "https://www.alphavantage.co/query"
        self.cache = ResponseCache()
        self.rate_limiter = RateLimiter(
            max_calls=RATE_LIMIT_CALLS_PER_MINUTE,
            time_window=60
        )
        self._total_calls = 0

    def _make_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """
        Make HTTP request to Alpha Vantage API with rate limiting.

        Args:
            params: Request parameters

        Returns:
            JSON response data

        Raises:
            Exception: If request fails
        """
        # Check rate limit
        if not self.rate_limiter.can_proceed():
            wait_time = self.rate_limiter.wait_time()
            logger.warning(f"Rate limit reached. Need to wait {wait_time:.1f}s")
            return format_error_response(
                ERROR_RATE_LIMIT,
                suggestion=f"Wait {int(wait_time) + 1} seconds before retrying"
            )

        # Add API key to params
        params["apikey"] = self.api_key

        try:
            logger.debug(f"API request: {params.get('function')} for {params.get('symbol', 'N/A')}")
            response = requests.get(
                self.base_url,
                params=params,
                timeout=API_REQUEST_TIMEOUT
            )
            response.raise_for_status()

            # Record successful call
            self.rate_limiter.record_call()
            self._total_calls += 1

            data = response.json()

            # Check for API errors
            if "Error Message" in data:
                logger.error(f"API error: {data['Error Message']}")
                return format_error_response(
                    data["Error Message"],
                    suggestion="Check if the symbol is valid"
                )

            if "Note" in data:
                logger.warning("API rate limit message received")
                return format_error_response(
                    ERROR_RATE_LIMIT,
                    details=data["Note"]
                )

            return data

        except requests.Timeout:
            logger.error("API request timeout")
            return format_error_response(
                "Request timeout",
                suggestion="Try again or check your network connection"
            )
        except requests.RequestException as e:
            logger.error(f"Network error: {str(e)}")
            return format_error_response(
                ERROR_NETWORK,
                details=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return format_error_response(
                "Unexpected error occurred",
                details=str(e)
            )

    def get_forex_quote(self, pair: str) -> Dict[str, Any]:
        """
        Get real-time forex quote.

        Args:
            pair: Forex pair (e.g., 'EURUSD')

        Returns:
            Quote data or error
        """
        cache_key = f"forex_quote_{pair}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        try:
            from_curr, to_curr = format_pair_for_alpha_vantage(pair)
        except ValueError as e:
            return format_error_response(str(e), symbol=pair)

        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_curr,
            "to_currency": to_curr,
        }

        data = self._make_request(params)

        if "error" in data:
            return data

        if "Realtime Currency Exchange Rate" in data:
            rate_data = data["Realtime Currency Exchange Rate"]
            result = {
                "symbol": pair,
                "asset_type": "forex",
                "price": safe_float(rate_data.get("5. Exchange Rate", 0)),
                "bid": safe_float(rate_data.get("8. Bid Price", rate_data.get("5. Exchange Rate", 0))),
                "ask": safe_float(rate_data.get("9. Ask Price", rate_data.get("5. Exchange Rate", 0))),
                "timestamp": rate_data.get("6. Last Refreshed", ""),
                "timezone": rate_data.get("7. Time Zone", "UTC")
            }
            self.cache.set(cache_key, result, CACHE_TTL_QUOTES)
            return result

        return format_error_response(ERROR_NO_DATA, symbol=pair)

    def get_crypto_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time crypto quote.

        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETH')

        Returns:
            Quote data or error
        """
        cache_key = f"crypto_quote_{symbol}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Remove USD suffix if present
        crypto_base = symbol.replace('USD', '') if symbol.endswith('USD') else symbol

        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": crypto_base,
            "to_currency": "USD",
        }

        data = self._make_request(params)

        if "error" in data:
            return data

        if "Realtime Currency Exchange Rate" in data:
            rate_data = data["Realtime Currency Exchange Rate"]
            price = safe_float(rate_data.get("5. Exchange Rate", 0))

            from ..config import CRYPTO_SPREAD_MULTIPLIER_BID, CRYPTO_SPREAD_MULTIPLIER_ASK

            result = {
                "symbol": symbol,
                "asset_type": "crypto",
                "price": price,
                "bid": price * CRYPTO_SPREAD_MULTIPLIER_BID,
                "ask": price * CRYPTO_SPREAD_MULTIPLIER_ASK,
                "timestamp": rate_data.get("6. Last Refreshed", ""),
                "timezone": rate_data.get("7. Time Zone", "UTC")
            }
            self.cache.set(cache_key, result, CACHE_TTL_QUOTES)
            return result

        return format_error_response(ERROR_NO_DATA, symbol=symbol)

    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time stock quote.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Quote data or error
        """
        cache_key = f"stock_quote_{symbol}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
        }

        data = self._make_request(params)

        if "error" in data:
            return data

        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            price = safe_float(quote.get("05. price", 0))

            result = {
                "symbol": symbol,
                "asset_type": "stock",
                "price": price,
                "bid": price,
                "ask": price,
                "open": safe_float(quote.get("02. open", 0)),
                "high": safe_float(quote.get("03. high", 0)),
                "low": safe_float(quote.get("04. low", 0)),
                "volume": int(safe_float(quote.get("06. volume", 0))),
                "previous_close": safe_float(quote.get("08. previous close", 0)),
                "change": safe_float(quote.get("09. change", 0)),
                "change_percent": quote.get("10. change percent", "0%"),
                "timestamp": quote.get("07. latest trading day", ""),
            }
            self.cache.set(cache_key, result, CACHE_TTL_QUOTES)
            return result

        return format_error_response(ERROR_NO_DATA, symbol=symbol)

    def get_historical_data_forex(
        self,
        pair: str,
        timeframe: str = "1h",
        outputsize: str = "compact"
    ) -> Dict[str, Any]:
        """Get historical forex data."""
        cache_key = f"forex_hist_{pair}_{timeframe}_{outputsize}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        try:
            from_curr, to_curr = format_pair_for_alpha_vantage(pair)
        except ValueError as e:
            return format_error_response(str(e), symbol=pair)

        interval = TIMEFRAME_MAP.get(timeframe, "60min")

        if interval in ["5min", "15min", "30min", "60min"]:
            params = {
                "function": "FX_INTRADAY",
                "from_symbol": from_curr,
                "to_symbol": to_curr,
                "interval": interval,
                "outputsize": outputsize,
            }
        else:
            params = {
                "function": "FX_DAILY",
                "from_symbol": from_curr,
                "to_symbol": to_curr,
                "outputsize": outputsize,
            }

        data = self._make_request(params)

        if "error" in data:
            return data

        # Find time series key
        ts_key = None
        for key in data.keys():
            if "Time Series" in key:
                ts_key = key
                break

        if ts_key and ts_key in data:
            result = {"success": True, "data": data[ts_key], "pair": pair}
            self.cache.set(cache_key, result, CACHE_TTL_HISTORICAL)
            return result

        return format_error_response(ERROR_NO_DATA, symbol=pair)

    def get_historical_data_stock(
        self,
        symbol: str,
        timeframe: str = "1h",
        outputsize: str = "compact"
    ) -> Dict[str, Any]:
        """
        Get historical stock data.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            timeframe: Timeframe ('5m', '15m', '30m', '1h', '4h', '1d')
            outputsize: 'compact' (100 points) or 'full' (full history)

        Returns:
            Historical OHLCV data or error
        """
        cache_key = f"stock_historical_{symbol}_{timeframe}_{outputsize}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        interval = TIMEFRAME_MAP.get(timeframe, "60min")

        if interval in ["5min", "15min", "30min", "60min"]:
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": interval,
                "outputsize": outputsize,
            }
        else:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": outputsize,
            }

        data = self._make_request(params)

        if "error" in data:
            return data

        # Find time series key
        ts_key = None
        for key in data.keys():
            if "Time Series" in key:
                ts_key = key
                break

        if ts_key and ts_key in data:
            result = {"success": True, "data": data[ts_key], "symbol": symbol}
            self.cache.set(cache_key, result, CACHE_TTL_HISTORICAL)
            return result

        return format_error_response(ERROR_NO_DATA, symbol=symbol)

    def get_historical_data_crypto(
        self,
        symbol: str,
        timeframe: str = "1h",
        outputsize: str = "compact"
    ) -> Dict[str, Any]:
        """
        Get historical crypto data.

        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETH')
            timeframe: Timeframe ('5m', '15m', '30m', '1h', '4h', '1d')
            outputsize: 'compact' (100 points) or 'full' (full history)

        Returns:
            Historical OHLCV data or error
        """
        cache_key = f"crypto_historical_{symbol}_{timeframe}_{outputsize}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Remove USD suffix if present
        crypto_base = symbol.replace('USD', '') if symbol.endswith('USD') else symbol

        interval = TIMEFRAME_MAP.get(timeframe, "60min")

        if interval in ["5min", "15min", "30min", "60min"]:
            params = {
                "function": "CRYPTO_INTRADAY",
                "symbol": crypto_base,
                "market": "USD",
                "interval": interval,
                "outputsize": outputsize,
            }
        else:
            params = {
                "function": "DIGITAL_CURRENCY_DAILY",
                "symbol": crypto_base,
                "market": "USD",
            }

        data = self._make_request(params)

        if "error" in data:
            return data

        # Find time series key
        ts_key = None
        for key in data.keys():
            if "Time Series" in key:
                ts_key = key
                break

        if ts_key and ts_key in data:
            result = {"success": True, "data": data[ts_key], "symbol": symbol}
            self.cache.set(cache_key, result, CACHE_TTL_HISTORICAL)
            return result

        return format_error_response(ERROR_NO_DATA, symbol=symbol)

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        return {
            "total_api_calls": self._total_calls,
            "cache_stats": self.cache.get_stats(),
            "rate_limit": {
                "max_per_minute": RATE_LIMIT_CALLS_PER_MINUTE,
                "current_window_calls": len(self.rate_limiter.calls),
                "wait_time_seconds": self.rate_limiter.wait_time()
            }
        }
