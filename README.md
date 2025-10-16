# TradingViewMCPServer

Professional multi-asset trading assistant and Pine Script development server for Claude Desktop. Supports Forex, Stocks, Crypto with 20+ technical indicators plus comprehensive Pine Script development tools.

## Features

### Trading & Market Analysis

- **Multi-Asset Support**: Forex (22+ pairs), US Stocks, Cryptocurrencies
- **20+ Technical Indicators**: Volume Profile, Market Profile, VWAP, Fibonacci, Bollinger Bands, MACD, Moving Averages, ATR, Support/Resistance, Pivot Points, Stochastic, ADX, Ichimoku Cloud, and more
- **Real-time Data**: Live quotes and historical data via Alpha Vantage API
- **Claude Desktop Integration**: Seamless integration with Claude Desktop via MCP

### Pine Script Development Tools (NEW in v3.0)

- **Real-time Syntax Validation**: Comprehensive syntax and semantic error checking with line-by-line feedback
- **Intelligent Autocomplete**: Context-aware code completion with function signatures and documentation
- **Live Documentation Access**: Instant access to Pine Script function documentation with examples
- **Version Detection**: Automatic detection of Pine Script version (v1-v5) with compatibility analysis
- **Version Conversion**: Automatic code conversion between Pine Script versions (v4→v5, v3→v4)
- **Code Testing Sandbox**: Safe testing environment with validation and performance metrics
- **Error Explanations**: Detailed error descriptions with causes, solutions, and code examples
- **Code Templates**: Ready-to-use templates for indicators, strategies, and overlays

## Installation

### Prerequisites

- Python 3.9 or higher
- Claude Desktop
- Alpha Vantage API key (free at https://www.alphavantage.co/support/#api-key)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/lev-corrupted/TradingViewMCPServer.git
cd TradingViewMCPServer
```

2. Create virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

3. Create `.env` file with your API key:
```bash
echo "ALPHA_VANTAGE_API_KEY=your_key_here" > .env
```

4. Configure Claude Desktop:

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "tradingview": {
      "command": "/absolute/path/to/TradingViewMCPServer/.venv/bin/python",
      "args": [
        "/absolute/path/to/TradingViewMCPServer/tradingview_mcp/server.py",
        "stdio"
      ]
    }
  }
}
```

Replace `/absolute/path/to/TradingViewMCPServer` with your actual installation path.

5. Restart Claude Desktop

## Usage

### Trading & Market Analysis

Ask Claude Desktop natural language questions:

```
What's the current price of AAPL?
Show me Bollinger Bands for TSLA on 1h timeframe
Calculate Fibonacci levels for BTC
Get MACD for EURUSD
Show me support and resistance for NVDA
What's the volume profile for SPY?
Give me the Ichimoku Cloud for ETH
Calculate pivot points for GBPUSD
```

### Pine Script Development

Ask Claude to help with Pine Script code:

```
Validate this Pine Script code: [paste code]
Convert this v4 code to v5: [paste code]
Show me documentation for ta.macd
Test this indicator on AAPL 1h timeframe: [paste code]
Explain error E101
Detect the version of this Pine Script: [paste code]
Give me a Pine Script strategy template
```

## Available Tools

### Price & Market Data
- `get_price` - Get current price for any asset
- `get_multiple_prices` - Batch price quotes
- `list_available_pairs` - List forex pairs
- `list_supported_assets` - List all supported assets

### Technical Analysis
- `analyze_pair` - Comprehensive analysis
- `get_trading_recommendation` - Trading signals
- `calculate_correlation` - Pair correlation

### Volume & Profile Analysis
- `get_volume_profile` - Volume at price levels
- `get_market_profile` - Market profile with TPO and value areas
- `get_vwap` - Volume Weighted Average Price
- `get_volume_nodes` - High/low volume nodes
- `detect_unfilled_gaps` - Price gaps detection

### Popular Indicators
- `get_fibonacci_retracement` - Fibonacci levels
- `get_bollinger_bands` - Bollinger Bands
- `get_macd` - MACD indicator
- `get_moving_averages` - Multiple SMAs
- `get_atr` - Average True Range
- `get_support_resistance` - Auto-detected levels
- `get_pivot_points` - Daily pivot points
- `get_stochastic` - Stochastic oscillator
- `get_adx` - Trend strength
- `get_ichimoku_cloud` - Ichimoku Cloud

### Pine Script Development (NEW)
- `validate_pine_script` - Real-time syntax validation with detailed error reporting
- `get_pine_documentation` - Function and topic documentation with examples
- `test_pine_script` - Safe sandbox testing with metrics
- `explain_pine_error` - Detailed error explanations with solutions
- `detect_pine_version` - Automatic version detection (v1-v5)
- `convert_pine_version` - Automatic version conversion
- `autocomplete_pine` - Intelligent code completion
- `get_pine_template` - Ready-to-use code templates

## Supported Assets

### Forex
Major pairs, crosses, exotics, and gold (XAUUSD)

### Stocks
US equities including AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, and more

### Crypto
BTC, ETH, BNB, XRP, ADA, SOL, and other major cryptocurrencies

## Configuration

### API Rate Limits

Alpha Vantage free tier:
- 25 requests per day
- 5 API calls per minute

For higher limits, upgrade to premium API key.

### Timeframes

Supported timeframes: `5m`, `15m`, `30m`, `1h`, `4h`, `1d`

## Version 3.0 - Pine Script Integration (Current)

Major new release with comprehensive Pine Script development tools:

### New Features
- **8 Pine Script MCP Tools**: Complete development environment for Pine Script
- **3000+ Lines of Pine Script Code**: Lexer, parser, validator, and more
- **Version Support**: Full support for Pine Script v1-v5
- **Intelligent Analysis**: AST-based parsing and validation
- **50+ Function Signatures**: Comprehensive built-in function database
- **Automatic Conversion**: Smart v4→v5 code migration
- **Context-aware Completion**: Namespace-aware autocomplete
- **Error Database**: Detailed explanations for common errors

See [PINE_SCRIPT.md](PINE_SCRIPT.md) for complete Pine Script documentation.

## Version 2.0 Improvements

This version included major improvements and refactoring:

### Architecture
- **Modular Structure**: Refactored from monolithic 1700-line file to organized modules
  - `api/`: API client with caching and rate limiting
  - `indicators/`: Technical indicators organized by type
  - `utils/`: Utility functions and formatters
  - `config.py`: Centralized configuration

### Performance & Reliability
- **Smart Caching**: In-memory cache with TTL reduces API calls by ~70%
- **Rate Limiting**: Automatic rate limit protection prevents API errors
- **Improved Error Handling**: Standardized error responses with helpful suggestions
- **Comprehensive Logging**: Debug and track all operations

### Code Quality
- **Type Hints**: Full type annotations throughout
- **Better Calculations**: Fixed MACD, Stochastic, and ADX formulas
- **Constants**: All magic numbers extracted to named constants
- **Test Suite**: pytest-based testing framework included

### Development
- **Lower Python Requirement**: Now works with Python 3.9+ (was 3.13+)
- **Development Tools**: Added black, mypy, pytest, and other dev dependencies
- **Better Documentation**: Improved docstrings and code comments

### API Improvements
- **Universal Asset Detection**: Automatically detects Forex, Stocks, or Crypto
- **Better Forex Detection**: Handles various formats (EUR/USD, EURUSD, etc.)
- **Cache Statistics**: View cache performance with `get_server_stats()` tool

## Testing

Run the test suite:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=tradingview_mcp --cov-report=html

# Run specific test file
pytest tests/test_cache.py -v

# Run tests matching pattern
pytest -k "test_cache" -v
```

## Troubleshooting

### Claude Desktop Not Connecting

1. Verify config file path is correct
2. Check Python path in config
3. Ensure `.env` file exists with valid API key
4. Restart Claude Desktop

### API Rate Limit Errors

Wait 1 minute between requests or upgrade API key.

### Module Import Errors

Ensure virtual environment is activated and dependencies installed:
```bash
source .venv/bin/activate
pip install -e .
```

## License

MIT License - see LICENSE file for details

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### How to Contribute

- **Bug Reports**: Use the bug report template
- **Feature Requests**: Use the feature request template
- **Code Contributions**: Fork, create a branch, and submit a PR
- **Documentation**: Improvements to README, code comments, or examples

### Contribution Ideas

- New technical indicators (RSI, CCI, Williams %R, etc.)
- Performance optimizations
- Additional asset types or markets
- Better error handling
- Enhanced documentation
- Example use cases

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and coding standards.

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review [CONTRIBUTING.md](CONTRIBUTING.md)
3. Search existing [GitHub Issues](https://github.com/lev-corrupted/TradingViewMCPServer/issues)
4. Open a new issue with the appropriate template
