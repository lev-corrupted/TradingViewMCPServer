"""Tests for technical indicators."""

import pytest
from tradingview_mcp.indicators.trend import calculate_moving_averages, calculate_ema
from tradingview_mcp.indicators.momentum import calculate_fibonacci_levels
from tradingview_mcp.indicators.volatility import calculate_atr, calculate_bollinger_bands
from tradingview_mcp.indicators.volume import calculate_vwap


class TestTrendIndicators:
    """Tests for trend indicators."""

    def test_calculate_ema(self):
        """Test EMA calculation."""
        prices = [10, 11, 12, 13, 14, 15]
        ema = calculate_ema(prices, period=3)

        assert isinstance(ema, float)
        assert ema > 0

    def test_moving_averages(self, sample_ohlcv_data):
        """Test moving averages calculation."""
        # Extend sample data for MA calculation
        extended_data = sample_ohlcv_data.copy()
        for i in range(6, 30):
            extended_data[f"2023-10-16 {i:02d}:00:00"] = {
                "1. open": "1.0800",
                "2. high": "1.0820",
                "3. low": "1.0790",
                "4. close": "1.0810",
                "5. volume": "1000"
            }

        result = calculate_moving_averages(extended_data)

        assert "current_price" in result
        assert "sma_20" in result or len(result) > 1  # At least some SMA calculated
        assert all(isinstance(v, (int, float)) for v in result.values())


class TestMomentumIndicators:
    """Tests for momentum indicators."""

    def test_fibonacci_levels(self, sample_ohlcv_data):
        """Test Fibonacci retracement calculation."""
        result = calculate_fibonacci_levels(sample_ohlcv_data)

        assert "swing_high" in result
        assert "swing_low" in result
        assert "50.0%" in result
        assert "61.8%" in result
        assert result["swing_high"] > result["swing_low"]


class TestVolatilityIndicators:
    """Tests for volatility indicators."""

    def test_atr_calculation(self, sample_ohlcv_data):
        """Test ATR calculation."""
        # Extend data for ATR
        extended_data = sample_ohlcv_data.copy()
        for i in range(6, 20):
            extended_data[f"2023-10-16 {i:02d}:00:00"] = {
                "1. open": "1.0800",
                "2. high": "1.0820",
                "3. low": "1.0790",
                "4. close": "1.0810",
                "5. volume": "1000"
            }

        result = calculate_atr(extended_data, period=14)

        assert "atr" in result
        assert "atr_percent" in result
        assert "volatility" in result
        assert result["atr"] > 0

    def test_bollinger_bands(self, sample_ohlcv_data):
        """Test Bollinger Bands calculation."""
        # Extend data
        extended_data = sample_ohlcv_data.copy()
        for i in range(6, 25):
            extended_data[f"2023-10-16 {i:02d}:00:00"] = {
                "1. open": "1.0800",
                "2. high": "1.0820",
                "3. low": "1.0790",
                "4. close": "1.0810",
                "5. volume": "1000"
            }

        result = calculate_bollinger_bands(extended_data, period=20)

        assert "upper_band" in result
        assert "middle_band" in result
        assert "lower_band" in result
        assert "percent_b" in result
        assert result["upper_band"] > result["middle_band"] > result["lower_band"]


class TestVolumeIndicators:
    """Tests for volume indicators."""

    def test_vwap_calculation(self, sample_ohlcv_data):
        """Test VWAP calculation."""
        vwap = calculate_vwap(sample_ohlcv_data)

        assert isinstance(vwap, float)
        assert vwap > 0
