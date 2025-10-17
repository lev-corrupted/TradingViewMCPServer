# Contributing to TradingViewMCPServer

Thank you for your interest in contributing to TradingViewMCPServer! This document provides guidelines for contributions.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment
- Support fellow contributors

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/TradingViewMCPServer.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/TradingViewMCPServer.git
cd TradingViewMCPServer

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Create .env file with your Alpha Vantage API key
echo "ALPHA_VANTAGE_API_KEY=your_key_here" > .env
```

## Project Structure

```
TradingViewMCPServer/
├── tradingview_mcp/
│   ├── __init__.py
│   └── server.py          # Main MCP server with all tools
├── .env                    # API credentials (not in repo)
├── .gitignore
├── LICENSE
├── README.md
├── CONTRIBUTING.md
└── pyproject.toml
```

## Guidelines

### Code Style

- Follow PEP 8 conventions
- Use type hints where applicable
- Add docstrings to all functions
- Keep functions focused and modular
- Use descriptive variable names

### Adding New Features

#### New Technical Indicators

When adding a new technical indicator:

1. Add the indicator calculation function
2. Register it as an MCP tool in `server.py`
3. Include proper error handling
4. Add documentation in the tool description
5. Test with multiple assets and timeframes

Example structure:
```python
def calculate_indicator(data, params):
    """
    Calculate technical indicator.

    Args:
        data: Price data
        params: Indicator parameters

    Returns:
        Calculated values
    """
    # Implementation here
    pass
```

#### New Asset Types

To add support for new asset types:

1. Update the asset validation logic
2. Add new symbols to supported lists
3. Update documentation
4. Test data fetching for new asset type

### Testing

- Test with real API calls (use your own API key)
- Verify all timeframes work correctly
- Test error handling (invalid symbols, API failures)
- Check rate limit handling
- Validate output formats

### API Usage

- Respect Alpha Vantage rate limits (5 calls/minute for free tier)
- Include appropriate delays between requests
- Handle API errors gracefully
- Cache results when possible
- Document any new API endpoints used

### Documentation

- Update README.md for user-facing changes
- Add code comments for complex logic
- Update tool descriptions in server.py
- Include usage examples for new features
- Document any new dependencies

## Pull Request Process

1. Ensure your code follows the style guidelines
2. Update documentation as needed
3. Test your changes thoroughly
4. Reference related issues in your PR description
5. Wait for review and address feedback
6. Keep your PR focused on a single feature/fix

## Types of Contributions

### Bug Reports

Use the bug report template and include:
- Python version
- OS and version
- Steps to reproduce
- Expected vs actual behavior
- Error logs
- Asset/symbol being tested

### Feature Requests

Use the feature request template and ensure the feature:
- Adds value to trading analysis
- Aligns with project goals
- Is technically feasible
- Doesn't violate Alpha Vantage terms

### Code Contributions

We welcome:
- New technical indicators
- Performance improvements
- Bug fixes
- Documentation improvements
- Error handling enhancements
- Test coverage
- API optimization

### What We Don't Accept

- Trading bots or automated trading features
- Features requiring paid API tiers without alternatives
- Breaking changes without migration path
- Code that violates Alpha Vantage terms of service
- Proprietary/closed-source indicators without permission

## Coding Standards

### Function Documentation

```python
def get_technical_indicator(
    symbol: str,
    interval: str,
    period: int
) -> dict:
    """
    Calculate technical indicator for given symbol.

    Args:
        symbol: Trading symbol (e.g., 'AAPL', 'EURUSD')
        interval: Time interval ('5m', '1h', '1d')
        period: Lookback period for calculation

    Returns:
        Dictionary containing indicator values and metadata

    Raises:
        ValueError: If symbol or interval is invalid
        APIError: If API request fails
    """
    pass
```

### Error Handling

```python
try:
    result = fetch_data(symbol)
except requests.RequestException as e:
    return {
        "error": "API request failed",
        "details": str(e),
        "suggestion": "Check your API key and network connection"
    }
```

### MCP Tool Registration

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls with proper error handling."""
    try:
        if name == "your_tool":
            result = your_function(**arguments)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
    except Exception as e:
        logger.error(f"Error in {name}: {str(e)}")
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]
```

## Testing Guidelines

### Manual Testing Checklist

- [ ] Test with forex pair (e.g., EURUSD)
- [ ] Test with stock symbol (e.g., AAPL)
- [ ] Test with cryptocurrency (e.g., BTC)
- [ ] Test all supported timeframes
- [ ] Test error handling (invalid symbol)
- [ ] Verify output format is valid JSON
- [ ] Check rate limiting doesn't cause errors
- [ ] Test with Claude Desktop integration

### Integration Testing

```bash
# Test the server directly
python tradingview_mcp/server.py stdio

# Test via Claude Desktop
# Ask Claude: "What's the current price of AAPL?"
```

## Versioning

We use semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

## Getting Help

- Open an issue with the "question" label
- Check existing issues and discussions
- Review the README and documentation
- Check Alpha Vantage documentation for API questions

## Recognition

Contributors will be:
- Listed in release notes
- Mentioned in significant feature additions
- Credited in documentation for major contributions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Open an issue with the label "question" or reach out via GitHub Discussions.

Thank you for contributing to TradingViewMCPServer!
