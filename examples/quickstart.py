#!/usr/bin/env python3
"""
Quick Start Demo

Run this to see the system in action!
"""

from backtester import quick_backtest
from strategies.ma_crossover import MACrossover

print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           FOREX BACKTESTING SYSTEM - QUICK START            ║
║                                                              ║
║   Testing MA Crossover Strategy on EUR/USD                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

# Run a quick backtest
quick_backtest(
    MACrossover,
    pair='EURUSD',
    start='2023-01-01',
    end='2024-01-01',
    show_plot=True
)

print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    NEXT STEPS                                ║
║                                                              ║
║  1. Run the interactive menu:                                ║
║     python strategy_manager.py                               ║
║                                                              ║
║  2. Read the complete guide:                                 ║
║     Open USER_GUIDE.md                                       ║
║                                                              ║
║  3. Create your own strategy:                                ║
║     cp strategies/template.py strategies/my_strategy.py      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")