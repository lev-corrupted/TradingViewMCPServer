# TradingViewMCPServer - Project Summary

## 📋 Overview

**TradingViewMCPServer** is a comprehensive Model Context Protocol (MCP) server that provides TWO powerful functionalities:

1. **TradingView Analysis Tools** - Real-time market data, technical indicators, and trading analysis
2. **Pine Script Development Tools** - Complete IDE-like environment for Pine Script development

### Current Version
**v3.1.0** - Latest with full Pine Script v6 support

---

## 🎯 Quick Reference

### Documentation Structure

```
TradingViewMCPServer/
├── README.md                    # Main documentation - Start here!
├── CHANGELOG.md                # Version history (consolidated)
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md         # Architecture details
│   ├── CONTRIBUTING.md         # How to contribute
│   ├── guides/                 # Usage guides
│   └── releases/               # Release notes
└── examples/                   # Example code
    └── pine-scripts/           # Pine Script strategies
        ├── README.md           # Strategy folder guide
        ├── indicators/         # Custom indicators
        ├── strategies/         # Trading strategies
        ├── overlays/           # Chart overlays
        └── examples/           # Example scripts
```

### Key Documentation

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [README.md](../README.md) | Main documentation, features, installation | First time setup, feature overview |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Project structure, design | Understanding codebase, contributing |
| [CHANGELOG.md](../CHANGELOG.md) | Version history | See what's new, migration |
| [guides/PINE_SCRIPT.md](guides/PINE_SCRIPT.md) | Pine Script tools guide | Developing Pine Script code |
| [releases/](releases/) | Version release notes | Understanding specific version updates |
| [examples/pine-scripts/README.md](../examples/pine-scripts/README.md) | Strategy organization | Storing your Pine Script code |

---

## 🚀 Features

### TradingView Analysis Tools

#### Market Data
- Multi-asset support (Forex, Stocks, Crypto)
- 22+ Forex pairs
- Real-time quotes
- Historical data

#### Technical Indicators (20+)
- Trend: MA, MACD, ADX, Ichimoku
- Momentum: Stochastic, RSI
- Volatility: Bollinger Bands, ATR
- Volume: VWAP, Volume Profile, Market Profile
- S/R: Support/Resistance, Pivot Points, Gaps

### Pine Script Development Tools (v1-v6 Support)

#### 8 MCP Tools
1. **validate_pine_script** - Real-time validation
2. **get_pine_documentation** - Function docs (110+ functions)
3. **test_pine_script** - Safe sandbox testing
4. **explain_pine_error** - Error explanations
5. **detect_pine_version** - Version detection (v1-v6)
6. **convert_pine_version** - Version conversion (v3→v4→v5→v6)
7. **autocomplete_pine** - Code completion
8. **get_pine_template** - Code templates

#### Pine Script v6 Features (LATEST!)
- **type** - Custom data structures (structs)
- **enum** - Enumeration types
- **map.*** - Key-value collections
- 11 new v6-specific functions
- Enhanced type system

---

## 📁 Project Structure

### Clean Modular Architecture

```
TradingViewMCPServer/
├── tradingview_mcp/              # Main package
│   ├── server.py                 # MCP server (orchestrator)
│   ├── config.py                 # Configuration
│   │
│   ├── api/                      # TradingView Analysis
│   │   ├── alpha_vantage.py      # API client
│   │   └── cache.py              # Caching layer
│   │
│   ├── indicators/               # TradingView Analysis
│   │   ├── trend.py              # MA, MACD, ADX, Ichimoku
│   │   ├── momentum.py           # Stochastic, RSI
│   │   ├── volatility.py         # Bollinger, ATR
│   │   ├── volume.py             # VWAP, Volume Profile
│   │   └── support_resistance.py # S/R, Pivots, Gaps
│   │
│   ├── utils/                    # TradingView Analysis
│   │   ├── asset_detector.py     # Asset type detection
│   │   └── formatters.py         # Response formatting
│   │
│   └── pine_script/              # Pine Script Tools (separate!)
│       ├── lexer.py              # Tokenization
│       ├── parser.py             # AST parsing
│       ├── validator.py          # Validation
│       ├── signatures.py         # Function database (110+)
│       ├── errors.py             # Error explanations
│       ├── documentation.py      # Docs system
│       ├── sandbox.py            # Testing
│       ├── versions.py           # Version tools
│       └── autocomplete.py       # Code completion
│
├── examples/                     # Example code
│   └── pine-scripts/            # Pine Script strategies
│       ├── indicators/
│       ├── strategies/
│       ├── overlays/
│       └── examples/
│
├── tests/                        # Test suite
│   ├── test_cache.py
│   ├── test_indicators.py
│   ├── test_pine_script.py
│   └── test_utils.py
│
├── docs/                         # Documentation (see above)
└── .venv/                        # Virtual environment
```

---

## 🎓 Quick Start Guide

### 1. Installation
```bash
cd TradingViewMCPServer
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Configuration
Create `.env` file:
```bash
echo "ALPHA_VANTAGE_API_KEY=your_key_here" > .env
```

Configure Claude Desktop:
```json
{
  "mcpServers": {
    "tradingview": {
      "command": "/path/to/.venv/bin/python",
      "args": ["/path/to/tradingview_mcp/server.py", "stdio"]
    }
  }
}
```

### 3. Usage

**TradingView Analysis:**
```
Ask Claude: "What's the current price of AAPL?"
Ask Claude: "Show me Bollinger Bands for BTC on 1h timeframe"
Ask Claude: "Calculate Fibonacci levels for EURUSD"
```

**Pine Script Development:**
```
Ask Claude: "Validate this Pine Script code: [code]"
Ask Claude: "Convert this v4 code to v6: [code]"
Ask Claude: "Show me documentation for map.new"
Ask Claude: "Create a MACD crossover strategy"
```

---

## 📊 Version History

### v3.1.0 (Current) - Pine Script v6 Support
- Full Pine Script v6 support
- 11 new v6 functions (type, enum, map.*)
- Architecture documentation
- Strategy folder organization
- Consolidated CHANGELOG

### v3.0.0 - Pine Script Integration
- 8 Pine Script MCP tools
- 3000+ lines of Pine Script code
- v1-v5 support
- 110+ function signatures

### v2.0.0 - Complete Refactoring
- Modular architecture (1700 → 12+ modules)
- Smart caching (70% fewer API calls)
- Rate limiting
- Test suite (60%+ coverage)

### v1.0.0 - Initial Release
- Basic forex trading assistant
- 20+ technical indicators
- Multi-asset support

---

## 🛠️ Development

### Running Tests
```bash
pip install -r requirements-dev.txt
pytest
pytest --cov=tradingview_mcp --cov-report=html
```

### Code Quality
```bash
black tradingview_mcp/    # Format
mypy tradingview_mcp/     # Type check
flake8 tradingview_mcp/   # Lint
```

### Contributing
1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Check [ARCHITECTURE.md](ARCHITECTURE.md)
3. Create feature branch
4. Add tests
5. Submit PR

---

## 🎯 Use Cases

### For Traders
- Get real-time market data
- Analyze technical indicators
- Test trading strategies
- Develop custom Pine Script indicators

### For Developers
- Build trading analysis tools
- Create custom MCP servers
- Learn Pine Script development
- Contribute to open source

### For Researchers
- Backtest strategies
- Analyze market data
- Study technical indicators
- Develop trading algorithms

---

## 📈 Statistics

### Code Metrics
- **Total Python Code**: 6000+ lines
- **Total Documentation**: 5000+ lines
- **Test Coverage**: 60%+
- **Modules**: 21
- **MCP Tools**: 36 (28 trading + 8 Pine Script)
- **Function Signatures**: 110+

### Performance
- **API Calls**: 70% reduction via caching
- **Error Rate**: 90% reduction via rate limiting
- **Validation Speed**: <500ms
- **Cache Hit Rate**: ~85%

---

## 🔗 Links

- **GitHub**: https://github.com/lev-corrupted/TradingViewMCPServer
- **Issues**: https://github.com/lev-corrupted/TradingViewMCPServer/issues
- **TradingView**: https://www.tradingview.com
- **Pine Script Docs**: https://www.tradingview.com/pine-script-docs/
- **Alpha Vantage**: https://www.alphavantage.co

---

## 📞 Support

### Getting Help
1. Check documentation (README.md, PINE_SCRIPT.md)
2. Review [CHANGELOG.md](CHANGELOG.md) for version info
3. Search [GitHub Issues](https://github.com/lev-corrupted/TradingViewMCPServer/issues)
4. Ask Claude using the MCP tools
5. Open a new issue with template

### Common Issues
- **Version Detection**: See [PINE_SCRIPT.md](PINE_SCRIPT.md)
- **Error Explanations**: Use `explain_pine_error()` tool
- **API Rate Limits**: Check cache settings in code
- **Installation Issues**: Verify Python 3.9+ and virtual environment

---

## 🎉 Key Achievements

✅ **Modular Architecture** - Clean separation of concerns
✅ **Pine Script v6 Support** - Latest version fully supported
✅ **Comprehensive Tools** - 36 MCP tools total
✅ **Well Documented** - 5000+ lines of documentation
✅ **Tested** - 60%+ code coverage
✅ **Performant** - 70% fewer API calls
✅ **Extensible** - Easy to add new features

---

## 🚀 Future Roadmap

### v3.2 (Next Minor)
- Enhanced v6 validation
- V6-specific error messages
- Additional tests
- Performance optimizations

### v4.0 (Next Major)
- Separate `tradingview_analysis/` module
- Separate `pine_script_tools/` module
- Lightweight orchestrator server
- Plugin system

---

## 📝 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- TradingView for Pine Script
- Alpha Vantage for market data API
- Anthropic for Claude and MCP
- Open source community

---

**Happy Trading & Coding!** 📊🚀

*Remember: Past performance does not guarantee future results. Use for educational purposes.*
