"""Tests for utility functions."""

import pytest
from tradingview_mcp.utils.asset_detector import detect_asset_type, format_pair_for_alpha_vantage
from tradingview_mcp.utils.formatters import format_error_response, safe_float, round_price


class TestAssetDetector:
    """Tests for asset type detection."""

    def test_detect_forex(self):
        """Test forex detection."""
        assert detect_asset_type("EURUSD") == ('forex', 'EURUSD')
        assert detect_asset_type("EUR/USD") == ('forex', 'EURUSD')
        assert detect_asset_type("XAUUSD") == ('forex', 'XAUUSD')

    def test_detect_crypto(self):
        """Test crypto detection."""
        assert detect_asset_type("BTC") == ('crypto', 'BTC')
        assert detect_asset_type("ETH") == ('crypto', 'ETH')
        assert detect_asset_type("BTCUSD") == ('crypto', 'BTC')

    def test_detect_stock(self):
        """Test stock detection."""
        assert detect_asset_type("AAPL") == ('stock', 'AAPL')
        assert detect_asset_type("MSFT") == ('stock', 'MSFT')
        assert detect_asset_type("GOOGL") == ('stock', 'GOOGL')

    def test_format_forex_pair(self):
        """Test forex pair formatting."""
        assert format_pair_for_alpha_vantage("EURUSD") == ('EUR', 'USD')
        assert format_pair_for_alpha_vantage("GBPJPY") == ('GBP', 'JPY')
        assert format_pair_for_alpha_vantage("XAUUSD") == ('XAU', 'USD')

    def test_format_invalid_pair(self):
        """Test that invalid pairs raise ValueError."""
        with pytest.raises(ValueError):
            format_pair_for_alpha_vantage("INVALID")


class TestFormatters:
    """Tests for formatting utilities."""

    def test_format_error_response(self):
        """Test error response formatting."""
        error = format_error_response("Test error", symbol="AAPL")

        assert error["error"] == "Test error"
        assert error["symbol"] == "AAPL"
        assert error["success"] is False

    def test_format_error_with_suggestion(self):
        """Test error response with suggestion."""
        error = format_error_response(
            "Rate limit reached",
            symbol="EURUSD",
            suggestion="Wait 1 minute"
        )

        assert error["suggestion"] == "Wait 1 minute"

    def test_safe_float(self):
        """Test safe float conversion."""
        assert safe_float("123.45") == 123.45
        assert safe_float("invalid", default=0.0) == 0.0
        assert safe_float(None, default=1.0) == 1.0
        assert safe_float(123) == 123.0

    def test_round_price(self):
        """Test price rounding."""
        assert round_price(1.23456789, 5) == 1.23457
        assert round_price(1.23456789, 2) == 1.23
        assert round_price(100.999, 0) == 101.0
