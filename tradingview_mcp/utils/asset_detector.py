"""Asset type detection and symbol formatting utilities."""

import logging
from typing import Tuple

from ..config import CRYPTO_SYMBOLS, FOREX_PAIRS, POPULAR_STOCKS

logger = logging.getLogger(__name__)


def detect_asset_type(symbol: str) -> Tuple[str, str]:
    """
    Detect asset type from symbol with improved logic.

    Args:
        symbol: Raw symbol input (e.g., 'EURUSD', 'AAPL', 'BTC', 'BTC/USD')

    Returns:
        Tuple of (asset_type, formatted_symbol)
        asset_type: 'forex', 'stock', or 'crypto'
        formatted_symbol: Cleaned and normalized symbol

    Examples:
        >>> detect_asset_type('EUR/USD')
        ('forex', 'EURUSD')
        >>> detect_asset_type('BTC-USD')
        ('crypto', 'BTC')
        >>> detect_asset_type('AAPL')
        ('stock', 'AAPL')
    """
    # Normalize: uppercase and remove separators
    original = symbol
    symbol = symbol.upper().replace("/", "").replace("_", "").replace("-", "")

    logger.debug(f"Detecting asset type for: {original} -> {symbol}")

    # Check crypto first (most specific patterns)
    # Pattern 1: Direct crypto symbol (BTC, ETH)
    if symbol in CRYPTO_SYMBOLS:
        logger.debug(f"{symbol} identified as crypto (direct match)")
        return ("crypto", symbol)

    # Pattern 2: Crypto with USD suffix (BTCUSD, ETHUSD)
    if symbol.endswith("USD") and len(symbol) > 3:
        base = symbol[:-3]
        if base in CRYPTO_SYMBOLS:
            logger.debug(f"{symbol} identified as crypto (USD pair)")
            return ("crypto", base)

    # Pattern 3: Crypto with USDT suffix (BTCUSDT)
    if symbol.endswith("USDT") and len(symbol) > 4:
        base = symbol[:-4]
        if base in CRYPTO_SYMBOLS:
            logger.debug(f"{symbol} identified as crypto (USDT pair)")
            return ("crypto", base)

    # Check forex (6 chars or special commodities)
    if symbol == "XAUUSD" or symbol in FOREX_PAIRS:
        logger.debug(f"{symbol} identified as forex (direct match)")
        return ("forex", symbol)

    if len(symbol) == 6:
        # Could be a forex pair
        from_curr = symbol[:3]
        to_curr = symbol[3:]
        # Check if both parts look like currencies (all letters)
        if from_curr.isalpha() and to_curr.isalpha():
            logger.debug(f"{symbol} identified as forex (6-char pattern)")
            return ("forex", symbol)

    # Check stocks
    if symbol in POPULAR_STOCKS:
        logger.debug(f"{symbol} identified as stock (direct match)")
        return ("stock", symbol)

    # Default: assume stock if alphanumeric and not matched above
    # This handles arbitrary stock symbols
    if symbol.replace(".", "").isalnum():
        logger.debug(f"{symbol} defaulting to stock (alphanumeric)")
        return ("stock", symbol)

    # Fallback
    logger.warning(
        f"Could not confidently detect asset type for {symbol}, defaulting to stock"
    )
    return ("stock", symbol)


def format_pair_for_alpha_vantage(pair: str) -> Tuple[str, str]:
    """
    Convert forex pair to Alpha Vantage format.

    Args:
        pair: Forex pair (e.g., 'EURUSD', 'XAUUSD')

    Returns:
        Tuple of (from_currency, to_currency)

    Raises:
        ValueError: If pair format is invalid

    Examples:
        >>> format_pair_for_alpha_vantage('EURUSD')
        ('EUR', 'USD')
        >>> format_pair_for_alpha_vantage('XAUUSD')
        ('XAU', 'USD')
    """
    # Handle gold
    if pair == "XAUUSD":
        return ("XAU", "USD")

    # Standard forex pairs (6 characters)
    if len(pair) == 6 and pair.isalpha():
        return (pair[:3], pair[3:])

    raise ValueError(
        f"Invalid forex pair format: {pair}. Expected 6 letters or 'XAUUSD'"
    )


def validate_symbol(symbol: str, asset_type: str) -> bool:
    """
    Validate if a symbol is reasonable for its asset type.

    Args:
        symbol: Symbol to validate
        asset_type: Expected asset type ('forex', 'stock', 'crypto')

    Returns:
        True if symbol appears valid for the asset type
    """
    if asset_type == "forex":
        return len(symbol) == 6 or symbol == "XAUUSD"
    elif asset_type == "crypto":
        return symbol in CRYPTO_SYMBOLS
    elif asset_type == "stock":
        # Stocks can be arbitrary, but check basic sanity
        return len(symbol) <= 10 and symbol.replace(".", "").isalnum()
    return False
