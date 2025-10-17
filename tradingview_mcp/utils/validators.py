"""
Input validation utilities for TradingView MCP Server.
"""

import re
from typing import Optional, Tuple
from ..config import TIMEFRAME_MAP, FOREX_PAIRS, POPULAR_STOCKS, CRYPTO_SYMBOLS


class ValidationError(Exception):
    """Custom validation error exception."""
    pass


def validate_timeframe(timeframe: str) -> Tuple[bool, Optional[str]]:
    """
    Validate timeframe parameter.

    Args:
        timeframe: Timeframe string (e.g., '5m', '1h', '1d')

    Returns:
        (is_valid, error_message)
    """
    if not timeframe:
        return False, "Timeframe cannot be empty"

    valid_timeframes = list(TIMEFRAME_MAP.keys())

    if timeframe not in valid_timeframes:
        return False, f"Invalid timeframe '{timeframe}'. Valid options: {', '.join(valid_timeframes)}"

    return True, None


def validate_symbol(symbol: str) -> Tuple[bool, Optional[str]]:
    """
    Validate symbol parameter.

    Args:
        symbol: Trading symbol

    Returns:
        (is_valid, error_message)
    """
    if not symbol:
        return False, "Symbol cannot be empty"

    # Clean up symbol
    cleaned_symbol = symbol.upper().replace("/", "").replace("_", "").replace(" ", "")

    # Check if it's a valid symbol format (alphanumeric, 2-12 characters)
    if not re.match(r'^[A-Z0-9]{2,12}$', cleaned_symbol):
        return False, f"Invalid symbol format '{symbol}'. Use alphanumeric characters only (2-12 chars)"

    # We allow any symbol - just validate format
    # The API will return an error if the symbol doesn't exist
    return True, None


def validate_period(period: int, min_val: int = 1, max_val: int = 500) -> Tuple[bool, Optional[str]]:
    """
    Validate period parameter for indicators.

    Args:
        period: Period value
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        (is_valid, error_message)
    """
    if not isinstance(period, int):
        return False, f"Period must be an integer, got {type(period).__name__}"

    if period < min_val or period > max_val:
        return False, f"Period must be between {min_val} and {max_val}, got {period}"

    return True, None


def validate_positive_number(value: float, name: str = "value") -> Tuple[bool, Optional[str]]:
    """
    Validate that a number is positive.

    Args:
        value: Number to validate
        name: Parameter name for error message

    Returns:
        (is_valid, error_message)
    """
    try:
        val = float(value)
        if val <= 0:
            return False, f"{name} must be positive, got {val}"
        return True, None
    except (TypeError, ValueError):
        return False, f"{name} must be a number, got {type(value).__name__}"


def validate_api_key(api_key: str) -> Tuple[bool, Optional[str]]:
    """
    Validate API key format.

    Args:
        api_key: API key string

    Returns:
        (is_valid, error_message)
    """
    if not api_key:
        return False, "API key is required"

    # Basic validation - Alpha Vantage keys are typically 16 alphanumeric chars
    if len(api_key) < 8:
        return False, "API key appears to be too short"

    if not re.match(r'^[A-Z0-9]+$', api_key.upper()):
        return False, "API key should contain only alphanumeric characters"

    return True, None
