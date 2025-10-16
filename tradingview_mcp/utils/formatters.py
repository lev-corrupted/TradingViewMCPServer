"""Response formatting utilities."""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def format_error_response(
    error: str,
    symbol: Optional[str] = None,
    details: Optional[str] = None,
    suggestion: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format a standardized error response.

    Args:
        error: Main error message
        symbol: Symbol that caused the error (optional)
        details: Additional error details (optional)
        suggestion: Suggestion for fixing the error (optional)

    Returns:
        Standardized error dictionary

    Example:
        >>> format_error_response(
        ...     "API rate limit reached",
        ...     symbol="AAPL",
        ...     suggestion="Wait 1 minute before retrying"
        ... )
        {'error': 'API rate limit reached', 'symbol': 'AAPL', 'suggestion': '...'}
    """
    response: Dict[str, Any] = {
        "error": error,
        "success": False
    }

    if symbol:
        response["symbol"] = symbol

    if details:
        response["details"] = details

    if suggestion:
        response["suggestion"] = suggestion

    logger.error(f"Error response: {response}")
    return response


def format_success_response(data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Format a standardized success response.

    Args:
        data: Main response data
        **kwargs: Additional fields to include

    Returns:
        Standardized success dictionary with success=True flag
    """
    response = {
        "success": True,
        **data,
        **kwargs
    }
    return response


def round_price(price: float, decimals: int = 5) -> float:
    """
    Round price to specified decimals.

    Args:
        price: Price value to round
        decimals: Number of decimal places (default 5 for forex)

    Returns:
        Rounded price
    """
    return round(price, decimals)


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a value as a percentage string.

    Args:
        value: Value to format (e.g., 0.0523 for 5.23%)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string (e.g., "5.23%")
    """
    return f"{value * 100:.{decimals}f}%"


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float with fallback.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Float value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert {value} to float, using default {default}")
        return default
