#!/usr/bin/env python3
"""
System Validation Script

Tests all components of the forex backtesting system to ensure
everything is working correctly.
"""

import sys
import os

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


def print_header(title):
    """Print a section header."""
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]{title}[/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")


def test_packages():
    """Test if all required packages are installed."""
    print_header("TEST 1: Package Installation")

    packages = [
        'pandas',
        'numpy',
        'backtesting',
        'yfinance',
        'talib',
        'bokeh',
        'matplotlib',
        'seaborn',
        'scipy',
        'rich'
    ]

    results = []
    all_passed = True

    for pkg in packages:
        try:
            __import__(pkg)
            results.append((pkg, "✅ PASS", "green"))
        except ImportError as e:
            results.append((pkg, f"❌ FAIL: {e}", "red"))
            all_passed = False

    # Display results
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Package", style="yellow")
    table.add_column("Status", style="white")

    for pkg, status, color in results:
        table.add_row(pkg, f"[{color}]{status}[/{color}]")

    console.print(table)

    if all_passed:
        console.print("\n[bold green]✅ All packages installed successfully![/bold green]")
    else:
        console.print("\n[bold red]❌ Some packages are missing. Please install them.[/bold red]")

    return all_passed


def test_strategy_discovery():
    """Test if strategies can be discovered."""
    print_header("TEST 2: Strategy Discovery")

    try:
        from strategies import discover_strategies

        strategies = discover_strategies()

        if len(strategies) == 0:
            console.print("[yellow]⚠️  No strategies found. This is OK if you haven't created any yet.[/yellow]")
            return True

        console.print(f"[green]✅ Found {len(strategies)} strategies:[/green]\n")

        for name, strategy_class in strategies.items():
            console.print(f"  • {name} ({strategy_class.__name__})")

        console.print(f"\n[bold green]✅ Strategy discovery working![/bold green]")
        return True

    except Exception as e:
        console.print(f"[red]❌ Strategy discovery failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


def test_data_download():
    """Test if data downloading works."""
    print_header("TEST 3: Data Download")

    try:
        from data.downloader import ForexDownloader

        console.print("Attempting to download sample data (EURUSD, last 30 days)...")

        downloader = ForexDownloader()
        data = downloader.download(
            'EURUSD',
            start='2024-01-01',
            end='2024-02-01',
            force_download=True
        )

        if data is not None and len(data) > 0:
            console.print(f"[green]✅ Downloaded {len(data)} bars of data[/green]")
            console.print(f"   Columns: {list(data.columns)}")
            console.print(f"   Date range: {data.index[0]} to {data.index[-1]}")
            console.print(f"\n[bold green]✅ Data download working![/bold green]")
            return True
        else:
            console.print("[red]❌ No data received[/red]")
            return False

    except Exception as e:
        console.print(f"[red]❌ Data download failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


def test_backtest():
    """Test if backtesting works."""
    print_header("TEST 4: Backtesting Engine")

    try:
        from backtesting import Backtest, Strategy
        from backtesting.lib import crossover
        import pandas as pd
        import yfinance as yf
        import talib

        console.print("Creating simple test strategy...")

        # Simple test strategy
        class TestStrategy(Strategy):
            fast_period = 10
            slow_period = 20

            def init(self):
                self.fast_ma = self.I(talib.SMA, self.data.Close, self.fast_period)
                self.slow_ma = self.I(talib.SMA, self.data.Close, self.slow_period)

            def next(self):
                if crossover(self.fast_ma, self.slow_ma):
                    if not self.position:
                        self.buy()
                elif crossover(self.slow_ma, self.fast_ma):
                    if self.position:
                        self.position.close()

        console.print("Downloading test data...")
        data = yf.download('EURUSD=X', start='2024-01-01', end='2024-03-01', progress=False)

        # Fix MultiIndex columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        data = data[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()

        console.print(f"Running backtest on {len(data)} bars...")
        bt = Backtest(data, TestStrategy, cash=10000, commission=0.0002)
        stats = bt.run()

        console.print(f"\n[green]✅ Backtest completed successfully![/green]")
        console.print(f"   Return: {stats['Return [%]']:.2f}%")
        console.print(f"   Trades: {stats['# Trades']}")
        console.print(f"   Sharpe Ratio: {stats.get('Sharpe Ratio', 0):.2f}")

        console.print(f"\n[bold green]✅ Backtesting engine working![/bold green]")
        return True

    except Exception as e:
        console.print(f"[red]❌ Backtest failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


def test_strategy_loading():
    """Test if example strategies can be loaded."""
    print_header("TEST 5: Strategy Loading")

    try:
        from strategies.ma_crossover import MACrossover
        from strategies.rsi_strategy import RSIStrategy
        from strategies.macd_strategy import MACDStrategy
        from strategies.bollinger_strategy import BollingerStrategy
        from strategies.multi_indicator import MultiIndicator

        strategies = [
            ('MA Crossover', MACrossover),
            ('RSI Strategy', RSIStrategy),
            ('MACD Strategy', MACDStrategy),
            ('Bollinger Strategy', BollingerStrategy),
            ('Multi Indicator', MultiIndicator)
        ]

        all_passed = True
        for name, strategy_class in strategies:
            try:
                # Check if class has required methods
                if not hasattr(strategy_class, 'init') or not hasattr(strategy_class, 'next'):
                    console.print(f"[yellow]⚠️  {name}: Missing init() or next() method[/yellow]")
                    all_passed = False
                else:
                    console.print(f"[green]✅ {name}: Loaded successfully[/green]")
            except Exception as e:
                console.print(f"[red]❌ {name}: Failed to load - {e}[/red]")
                all_passed = False

        if all_passed:
            console.print(f"\n[bold green]✅ All example strategies loaded![/bold green]")
        else:
            console.print(f"\n[yellow]⚠️  Some strategies have issues[/yellow]")

        return all_passed

    except Exception as e:
        console.print(f"[red]❌ Strategy loading failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


def test_full_system():
    """Test a complete backtest using the system."""
    print_header("TEST 6: Full System Integration")

    try:
        from backtester import ForexBacktester
        from strategies.ma_crossover import MACrossover

        console.print("Running full system test with MA Crossover on EURUSD...")

        backtester = ForexBacktester()
        stats = backtester.run(
            strategy=MACrossover,
            pair='EURUSD',
            start='2024-01-01',
            end='2024-03-01',
            show_plot=False
        )

        console.print(f"\n[green]✅ Full system test passed![/green]")
        console.print(f"   Strategy: MA Crossover")
        console.print(f"   Pair: EURUSD")
        console.print(f"   Return: {stats['Return [%]']:.2f}%")
        console.print(f"   Trades: {stats['# Trades']}")

        console.print(f"\n[bold green]✅ System integration working![/bold green]")
        return True

    except Exception as e:
        console.print(f"[red]❌ Full system test failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all validation tests."""
    console.clear()

    # Welcome banner
    panel = Panel(
        "[bold yellow]Forex Backtesting System - Validation Tests[/bold yellow]\n\n"
        "This will test all components of the system to ensure everything is working correctly.",
        title="System Validator",
        border_style="cyan"
    )
    console.print(panel)

    # Run tests
    tests = [
        ("Package Installation", test_packages),
        ("Strategy Discovery", test_strategy_discovery),
        ("Data Download", test_data_download),
        ("Backtesting Engine", test_backtest),
        ("Strategy Loading", test_strategy_loading),
        ("Full System Integration", test_full_system),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            console.print(f"[red]❌ Test '{test_name}' crashed: {e}[/red]")
            results.append((test_name, False))

    # Summary
    print_header("TEST SUMMARY")

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Test", style="yellow")
    table.add_column("Result", style="white")

    all_passed = True
    for test_name, passed in results:
        if passed:
            table.add_row(test_name, "[green]✅ PASS[/green]")
        else:
            table.add_row(test_name, "[red]❌ FAIL[/red]")
            all_passed = False

    console.print(table)

    # Final verdict
    console.print()
    if all_passed:
        console.print(Panel(
            "[bold green]🎉 ALL TESTS PASSED! 🎉[/bold green]\n\n"
            "Your forex backtesting system is fully operational.\n"
            "You can now run: [cyan]python strategy_manager.py[/cyan]",
            border_style="green"
        ))
        return 0
    else:
        console.print(Panel(
            "[bold red]⚠️  SOME TESTS FAILED[/bold red]\n\n"
            "Please review the errors above and fix any issues.\n"
            "Check PROJECT_NOTES.md for troubleshooting tips.",
            border_style="red"
        ))
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)