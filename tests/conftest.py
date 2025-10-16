"""Pytest configuration and fixtures."""

import pytest
from tradingview_mcp.api import ResponseCache, AlphaVantageClient


@pytest.fixture
def sample_ohlcv_data():
    """Sample OHLCV data for testing indicators."""
    return {
        "2023-10-16 10:00:00": {
            "1. open": "1.0850",
            "2. high": "1.0880",
            "3. low": "1.0840",
            "4. close": "1.0870",
            "5. volume": "1000"
        },
        "2023-10-16 09:00:00": {
            "1. open": "1.0840",
            "2. high": "1.0860",
            "3. low": "1.0830",
            "4. close": "1.0850",
            "5. volume": "1200"
        },
        "2023-10-16 08:00:00": {
            "1. open": "1.0830",
            "2. high": "1.0850",
            "3. low": "1.0820",
            "4. close": "1.0840",
            "5. volume": "900"
        },
        "2023-10-16 07:00:00": {
            "1. open": "1.0820",
            "2. high": "1.0840",
            "3. low": "1.0810",
            "4. close": "1.0830",
            "5. volume": "1100"
        },
        "2023-10-16 06:00:00": {
            "1. open": "1.0810",
            "2. high": "1.0830",
            "3. low": "1.0800",
            "4. close": "1.0820",
            "5. volume": "1300"
        },
    }


@pytest.fixture
def cache():
    """Fresh cache instance for testing."""
    return ResponseCache()


@pytest.fixture
def mock_api_response():
    """Mock API response for testing."""
    return {
        "Realtime Currency Exchange Rate": {
            "1. From_Currency Code": "EUR",
            "2. From_Currency Name": "Euro",
            "3. To_Currency Code": "USD",
            "4. To_Currency Name": "United States Dollar",
            "5. Exchange Rate": "1.08500",
            "6. Last Refreshed": "2023-10-16 10:00:00",
            "7. Time Zone": "UTC",
            "8. Bid Price": "1.08490",
            "9. Ask Price": "1.08510"
        }
    }
