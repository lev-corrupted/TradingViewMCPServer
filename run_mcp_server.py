#!/usr/bin/env python3
"""
MCP Server Runner

Wrapper script to run the TradingView MCP server with proper Python path.
"""

import sys
import os

# Add mcp_server to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mcp_server'))

# Import and run the server
from tradingview_mcp.server import main

if __name__ == "__main__":
    main()
