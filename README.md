# TradingViewMCPServer

Multi-asset trading assistant MCP server for Claude Desktop. Supports Forex, Stocks, and Crypto with 20+ technical indicators.

## Features

- **Multi-Asset Support**: Forex (22+ pairs), US Stocks, Cryptocurrencies
- **20+ Technical Indicators**: Volume Profile, Market Profile, VWAP, Fibonacci, Bollinger Bands, MACD, Moving Averages, ATR, Support/Resistance, Pivot Points, Stochastic, ADX, Ichimoku Cloud, and more
- **Real-time Data**: Live quotes and historical data via Alpha Vantage API
- **Claude Desktop Integration**: Seamless integration with Claude Desktop via MCP

## Installation

### Prerequisites

- Python 3.13 or higher
- Claude Desktop
- Alpha Vantage API key (free at https://www.alphavantage.co/support/#api-key)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/TradingViewMCPServer.git
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

Contributions welcome. Please open an issue or submit a pull request.
