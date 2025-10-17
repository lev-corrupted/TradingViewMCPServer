# TradingViewMCPServer Architecture

## Overview

TradingViewMCPServer is a comprehensive MCP (Model Context Protocol) server that provides **two distinct but complementary functionalities**:

1. **TradingView Analysis**: Real-time market data, technical indicators, and trading analysis for Forex, Stocks, and Crypto
2. **Pine Script Development Tools**: Complete IDE-like tooling for Pine Script development (v1-v6 support)

## Current Architecture (v3.1)

### Project Structure

```
TradingViewMCPServer/
├── tradingview_mcp/              # Main package (unified)
│   ├── server.py                 # MCP server (1300+ lines, handles both domains)
│   ├── config.py                 # Configuration
│   ├── __init__.py
│   │
│   ├── api/                      # TradingView Analysis: API clients
│   │   ├── __init__.py
│   │   ├── alpha_vantage.py      # Alpha Vantage API client
│   │   └── cache.py              # Caching layer
│   │
│   ├── indicators/               # TradingView Analysis: Technical indicators
│   │   ├── __init__.py
│   │   ├── trend.py              # Trend indicators (MA, MACD, ADX, Ichimoku)
│   │   ├── momentum.py           # Momentum indicators (RSI, Stochastic)
│   │   ├── volatility.py         # Volatility indicators (BB, ATR)
│   │   ├── volume.py             # Volume indicators (VWAP, Volume Profile)
│   │   └── support_resistance.py # S/R detection, pivots, gaps
│   │
│   ├── utils/                    # TradingView Analysis: Utilities
│   │   ├── __init__.py
│   │   ├── asset_detector.py     # Asset type detection (Forex/Stock/Crypto)
│   │   └── formatters.py         # Response formatters
│   │
│   └── pine_script/              # Pine Script Tools (separate concern)
│       ├── __init__.py
│       ├── lexer.py              # Tokenization (500+ lines)
│       ├── parser.py             # AST generation (600+ lines)
│       ├── validator.py          # Syntax validation (200+ lines)
│       ├── signatures.py         # Function database (900+ lines, 110+ functions)
│       ├── errors.py             # Error explanations (300+ lines)
│       ├── documentation.py      # Docs system (200+ lines)
│       ├── sandbox.py            # Testing environment (200+ lines)
│       ├── versions.py           # Version detection/conversion (500+ lines)
│       └── autocomplete.py       # Intelligent completion (300+ lines)
│
├── tests/                        # Test suite
│   ├── test_cache.py
│   ├── test_indicators.py
│   ├── test_pine_script.py
│   └── test_utils.py
│
├── README.md                     # Main documentation
├── PINE_SCRIPT.md               # Pine Script specific docs
├── ARCHITECTURE.md              # This file
├── CHANGELOG.md
└── setup.py
```

### Key Characteristics

**Unified but Modular:**
- Single MCP server exposes both TradingView analysis and Pine Script tools
- Clear separation within codebase (api/, indicators/, utils/ vs pine_script/)
- Shared infrastructure (logging, caching, error handling)

**Benefits:**
- ✅ Single installation and configuration
- ✅ Unified authentication and API management
- ✅ Shared caching and rate limiting
- ✅ One server to manage in Claude Desktop
- ✅ Clear module boundaries within codebase

**Concerns:**
- ❌ Large server.py file (1300+ lines)
- ❌ Mixing two distinct domains in one module
- ❌ Potential for tighter coupling over time

## Proposed Architecture (Future v4.0)

### Enhanced Modular Structure

To improve maintainability while preserving the unified MCP server approach:

```
TradingViewMCPServer/
├── tradingview_analysis/         # TradingView Analysis Module (NEW)
│   ├── __init__.py
│   ├── server_tools.py           # MCP tool definitions for trading
│   ├── api/
│   │   ├── alpha_vantage.py
│   │   └── cache.py
│   ├── indicators/
│   │   ├── trend.py
│   │   ├── momentum.py
│   │   ├── volatility.py
│   │   ├── volume.py
│   │   └── support_resistance.py
│   └── utils/
│       ├── asset_detector.py
│       └── formatters.py
│
├── pine_script_tools/            # Pine Script Module (NEW)
│   ├── __init__.py
│   ├── server_tools.py           # MCP tool definitions for Pine Script
│   ├── parser/
│   │   ├── lexer.py
│   │   └── parser.py
│   ├── validator/
│   │   ├── validator.py
│   │   └── signatures.py
│   ├── autocomplete/
│   │   └── autocomplete.py
│   ├── documentation/
│   │   ├── documentation.py
│   │   └── errors.py
│   └── versions/
│       ├── versions.py
│       └── sandbox.py
│
├── tradingview_mcp/              # Main MCP Server (Orchestrator)
│   ├── __init__.py
│   ├── server.py                 # Lightweight orchestrator (<300 lines)
│   ├── config.py                 # Shared configuration
│   └── shared/
│       ├── logging.py
│       └── error_handling.py
│
├── docs/                         # Documentation
│   ├── trading_analysis.md      # TradingView analysis docs
│   ├── pine_script.md           # Pine Script tool docs
│   └── architecture.md          # This file
│
└── tests/
    ├── trading_analysis/
    └── pine_script_tools/
```

### Benefits of Proposed Structure

1. **Clear Separation of Concerns**
   - Each module is truly independent
   - Can develop/test/maintain separately
   - Easier to understand for contributors

2. **Better Code Organization**
   - Smaller, focused files
   - Logical grouping by functionality
   - Easier navigation

3. **Improved Testing**
   - Test each module independently
   - Clearer test organization
   - Better test coverage tracking

4. **Future Extensibility**
   - Easy to add new modules (e.g., Backtest Tools, Chart Rendering)
   - Can version modules independently
   - Potential to publish modules separately

5. **Maintained User Experience**
   - Still single MCP server for users
   - Same configuration approach
   - No changes to Claude Desktop setup

## Implementation Plan

### Phase 1: Current State (v3.1) ✅ DONE
- Pine Script v6 support
- Enhanced function database (110+ functions)
- Improved documentation
- Bug fixes and optimizations

### Phase 2: Documentation & Planning ✅ CURRENT
- Document current architecture
- Create detailed migration plan
- Get feedback from users/contributors

### Phase 3: Gradual Migration (v3.2)
- Extract TradingView analysis tools to separate module
- Extract Pine Script tools to separate module
- Keep backward compatibility
- Comprehensive testing

### Phase 4: Server Refactoring (v4.0)
- Refactor server.py to be lightweight orchestrator
- Update documentation
- Migration guide for contributors
- Performance benchmarking

## Design Principles

### 1. Separation of Concerns
- Trading analysis logic separate from Pine Script logic
- Clear module boundaries
- Minimal cross-module dependencies

### 2. Single Responsibility
- Each module handles one domain
- Small, focused functions
- Logical grouping

### 3. Unified User Experience
- Single MCP server
- Consistent API design
- Unified error handling and logging

### 4. Maintainability
- Clear code organization
- Comprehensive documentation
- Extensive test coverage

### 5. Extensibility
- Easy to add new features
- Modular design allows independent development
- Plugin-like architecture

## Module Interfaces

### TradingView Analysis Module

**Exports:**
- `register_trading_tools(mcp_server)` - Register all trading MCP tools
- Data access classes (API clients, cache)
- Indicator calculation functions

**MCP Tools:**
- Price & market data tools (get_price, get_multiple_prices, etc.)
- Technical analysis tools (analyze_pair, calculate_correlation, etc.)
- Indicator tools (get_fibonacci, get_bollinger_bands, etc.)
- Volume analysis tools (get_vwap, get_volume_profile, etc.)

### Pine Script Tools Module

**Exports:**
- `register_pine_tools(mcp_server)` - Register all Pine Script MCP tools
- Validator, parser, lexer classes
- Documentation and autocomplete systems

**MCP Tools:**
- validate_pine_script
- get_pine_documentation
- test_pine_script
- explain_pine_error
- detect_pine_version
- convert_pine_version
- autocomplete_pine
- get_pine_template

### Main Server (Orchestrator)

**Responsibilities:**
- Initialize MCP server
- Register all tools from both modules
- Handle global configuration
- Manage logging and error handling
- Coordinate shared resources (cache, API clients)

## Migration Strategy

### For Users
- **No action required** - Same configuration, same tools
- Only benefit: Better performance and stability

### For Contributors
- **Phase 1**: Familiarize with new structure
- **Phase 2**: Update import paths in contributions
- **Phase 3**: Follow new module guidelines

### Backward Compatibility
- All existing tools remain available
- No breaking changes to MCP interface
- Import paths maintained with deprecation warnings

## Performance Considerations

### Current Performance
- Single process server
- Shared cache and API clients
- ~200-500ms average response time

### Expected After Migration
- Same or better performance
- Better memory management (module isolation)
- Improved caching strategies
- Potential for future parallelization

## Security Considerations

### Current Security
- API keys in environment variables
- No data persistence beyond cache
- Read-only operations (defensive security compliant)

### Maintained in New Architecture
- Same security model
- Module isolation adds defense in depth
- Clearer audit trails per module

## Conclusion

The proposed architecture maintains the unified MCP server approach while dramatically improving code organization, maintainability, and extensibility. The migration will be gradual and transparent to users, with comprehensive testing at each phase.

**Current Status**: v3.1 - Pine Script v6 support, documentation improved
**Next Step**: Community feedback and planning for v3.2 migration

---

**Questions or Feedback?**
- Open an issue: https://github.com/lev-corrupted/TradingViewMCPServer/issues
- Read contributing guide: CONTRIBUTING.md
