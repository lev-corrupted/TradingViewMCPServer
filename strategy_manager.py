#!/usr/bin/env python3
"""
Strategy Manager - Interactive CLI

Beautiful command-line interface for managing and running forex strategies.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress
from rich import box
from rich.layout import Layout
from rich.text import Text

from datetime import datetime, timedelta
from typing import Optional, List
import sys

from strategies import discover_strategies
from backtester import ForexBacktester
from utils.data_loader import DataLoader
from utils.performance import PerformanceAnalyzer, print_summary
from data.downloader import FOREX_PAIRS
from forex_config import DEFAULT_TIMEFRAMES, AVAILABLE_TIMEFRAMES


console = Console()


class StrategyManager:
    """Interactive CLI for managing forex strategies."""

    def __init__(self):
        self.backtester = ForexBacktester()
        self.data_loader = DataLoader()
        self.strategies = discover_strategies()

    def run(self):
        """Main entry point for CLI."""
        self.show_welcome()

        while True:
            try:
                choice = self.show_main_menu()

                if choice == '1':
                    self.run_single_strategy()
                elif choice == '2':
                    self.compare_strategies()
                elif choice == '3':
                    self.test_on_multiple_pairs()
                elif choice == '4':
                    self.optimize_strategy()
                elif choice == '5':
                    self.list_strategies()
                elif choice == '6':
                    self.download_data()
                elif choice == '7':
                    self.show_help()
                elif choice == '8' or choice.lower() == 'q':
                    self.exit_program()
                else:
                    console.print("[red]Invalid choice. Please try again.[/red]")

            except KeyboardInterrupt:
                console.print("\n[yellow]Operation cancelled.[/yellow]")
                continue
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                continue

    def show_welcome(self):
        """Display welcome banner."""
        console.clear()

        welcome = Text()
        welcome.append("\n")
        welcome.append("╔═══════════════════════════════════════════════════════╗\n", style="bold cyan")
        welcome.append("║                                                       ║\n", style="bold cyan")
        welcome.append("║           ", style="bold cyan")
        welcome.append("FOREX STRATEGY BACKTESTER", style="bold yellow")
        welcome.append("              ║\n", style="bold cyan")
        welcome.append("║                                                       ║\n", style="bold cyan")
        welcome.append("║   ", style="bold cyan")
        welcome.append("Test, Compare, and Optimize Trading Strategies", style="bold white")
        welcome.append("   ║\n", style="bold cyan")
        welcome.append("║                                                       ║\n", style="bold cyan")
        welcome.append("╚═══════════════════════════════════════════════════════╝\n", style="bold cyan")
        welcome.append("\n")

        console.print(welcome)
        console.print(f"[dim]Discovered {len(self.strategies)} strategies[/dim]\n")

    def show_main_menu(self) -> str:
        """Display main menu and get user choice."""
        console.print("\n[bold cyan]═══ MAIN MENU ═══[/bold cyan]\n")

        menu_items = [
            ("1", "Run Single Strategy", "Test one strategy on one pair"),
            ("2", "Compare Strategies", "Compare multiple strategies"),
            ("3", "Test on Multiple Pairs", "Test one strategy on multiple pairs"),
            ("4", "Optimize Strategy", "Find best parameters"),
            ("5", "List Strategies", "Show all available strategies"),
            ("6", "Download Data", "Download forex data"),
            ("7", "Help", "Show usage guide"),
            ("8", "Exit", "Quit the program"),
        ]

        for num, title, desc in menu_items:
            console.print(f"  [bold cyan]{num}.[/bold cyan] {title:<25} [dim]{desc}[/dim]")

        console.print()
        choice = Prompt.ask("[bold]Select option[/bold]", default="1")
        return choice

    def run_single_strategy(self):
        """Run a single strategy on a single pair."""
        console.print("\n[bold cyan]═══ RUN SINGLE STRATEGY ═══[/bold cyan]\n")

        # Select strategy
        strategy_name = self.select_strategy()
        if not strategy_name:
            return

        strategy_class = self.strategies[strategy_name]

        # Select pair
        pair = self.select_pair()
        if not pair:
            return

        # Select timeframe
        timeframe = self.select_timeframe()

        # Get date range
        start, end = self.get_date_range(timeframe)

        # Ask about plot
        show_plot = Confirm.ask("Show interactive plot?", default=True)

        # Run backtest
        console.print(f"\n[bold green]🚀 Running {strategy_name} on {pair} ({timeframe})...[/bold green]\n")

        try:
            stats = self.backtester.run(
                strategy=strategy_class,
                pair=pair,
                start=start,
                end=end,
                timeframe=timeframe,
                show_plot=show_plot
            )

            # Display results
            self.display_results(stats, f"{strategy_name} on {pair} ({timeframe})")

        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")

        input("\nPress Enter to continue...")

    def compare_strategies(self):
        """Compare multiple strategies on the same pair."""
        console.print("\n[bold cyan]═══ COMPARE STRATEGIES ═══[/bold cyan]\n")

        # Select multiple strategies
        selected_strategies = self.select_multiple_strategies()
        if not selected_strategies:
            return

        # Select pair
        pair = self.select_pair()
        if not pair:
            return

        # Select timeframe
        timeframe = self.select_timeframe()

        # Get date range
        start, end = self.get_date_range(timeframe)

        # Run comparison
        console.print(f"\n[bold green]🚀 Comparing {len(selected_strategies)} strategies on {pair} ({timeframe})...[/bold green]\n")

        try:
            results = self.backtester.run_multiple(
                strategies=selected_strategies,
                pair=pair,
                start=start,
                end=end,
                timeframe=timeframe,
                compare=False
            )

            # Display comparison table
            self.display_comparison(results, f"Strategy Comparison - {pair} ({timeframe})")

        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")

        input("\nPress Enter to continue...")

    def test_on_multiple_pairs(self):
        """Test one strategy on multiple pairs."""
        console.print("\n[bold cyan]═══ TEST ON MULTIPLE PAIRS ═══[/bold cyan]\n")

        # Select strategy
        strategy_name = self.select_strategy()
        if not strategy_name:
            return

        strategy_class = self.strategies[strategy_name]

        # Select multiple pairs
        pairs = self.select_multiple_pairs()
        if not pairs:
            return

        # Select timeframe
        timeframe = self.select_timeframe()

        # Get date range
        start, end = self.get_date_range(timeframe)

        # Run on all pairs
        console.print(f"\n[bold green]🚀 Testing {strategy_name} on {len(pairs)} pairs ({timeframe})...[/bold green]\n")

        try:
            results = self.backtester.run_on_multiple_pairs(
                strategy=strategy_class,
                pairs=pairs,
                start=start,
                end=end,
                timeframe=timeframe,
                compare=False
            )

            # Display comparison table
            self.display_comparison(results, f"{strategy_name} ({timeframe}) - Pair Comparison")

        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")

        input("\nPress Enter to continue...")

    def optimize_strategy(self):
        """Optimize strategy parameters."""
        console.print("\n[bold cyan]═══ OPTIMIZE STRATEGY ═══[/bold cyan]\n")

        console.print("[yellow]Parameter optimization feature coming soon![/yellow]")
        console.print("This will allow you to automatically find the best parameters for your strategy.\n")

        input("Press Enter to continue...")

    def list_strategies(self):
        """Display all available strategies."""
        console.print("\n[bold cyan]═══ AVAILABLE STRATEGIES ═══[/bold cyan]\n")

        if not self.strategies:
            console.print("[yellow]No strategies found![/yellow]")
            console.print("Create strategies in the strategies/ folder.\n")
        else:
            table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
            table.add_column("Strategy Name", style="green", no_wrap=True)
            table.add_column("Description", style="white")

            for name, strategy_class in self.strategies.items():
                doc = strategy_class.__doc__ or "No description available"
                # Get first line of docstring
                desc = doc.strip().split('\n')[0]
                table.add_row(name, desc)

            console.print(table)
            console.print()

        input("Press Enter to continue...")

    def download_data(self):
        """Download forex data."""
        console.print("\n[bold cyan]═══ DOWNLOAD FOREX DATA ═══[/bold cyan]\n")

        # Select pairs to download
        pairs = self.select_multiple_pairs()
        if not pairs:
            return

        # Get date range
        start, end = self.get_date_range()

        # Download
        console.print(f"\n[bold green]📥 Downloading {len(pairs)} pairs...[/bold green]\n")

        for pair in pairs:
            try:
                data = self.data_loader.load(pair, start, end, source='download')
                console.print(f"[green]✅ {pair}: {len(data)} bars downloaded[/green]")
            except Exception as e:
                console.print(f"[red]❌ {pair}: {e}[/red]")

        console.print("\n[green]Download complete![/green]")
        input("\nPress Enter to continue...")

    def show_help(self):
        """Display help information."""
        console.print("\n[bold cyan]═══ HELP & USAGE GUIDE ═══[/bold cyan]\n")

        help_text = """
[bold]Quick Start:[/bold]
1. Select "Run Single Strategy" from the main menu
2. Choose a strategy (e.g., MACrossover)
3. Choose a forex pair (e.g., EURUSD)
4. Set date range or use defaults
5. View results and charts!

[bold]Creating New Strategies:[/bold]
1. Copy strategies/template.py to strategies/your_strategy.py
2. Edit the file and fill in init() and next() methods
3. Run strategy_manager.py - it will be auto-discovered!

[bold]Available Forex Pairs:[/bold]
Majors: EURUSD, GBPUSD, USDJPY, AUDUSD, NZDUSD
High Vol: GBPJPY, EURJPY, AUDJPY, NZDJPY
Exotics: USDTRY, USDZAR (use with caution)

[bold]Tips:[/bold]
- Start with 1-2 years of data for testing
- Compare strategies before trusting them
- Test on multiple pairs to verify robustness
- Use parameter optimization to fine-tune strategies

[bold]Files:[/bold]
- strategies/ - All strategy files
- data/csv/ - Cached forex data
- USER_GUIDE.md - Complete user guide (read this!)
        """

        console.print(Panel(help_text, border_style="cyan"))
        input("\nPress Enter to continue...")

    def exit_program(self):
        """Exit the program."""
        console.print("\n[bold cyan]Thank you for using Forex Strategy Backtester![/bold cyan]")
        console.print("[dim]Happy trading! 🚀[/dim]\n")
        sys.exit(0)

    # ===== HELPER METHODS =====

    def select_strategy(self) -> Optional[str]:
        """Let user select a strategy."""
        if not self.strategies:
            console.print("[red]No strategies available![/red]")
            return None

        console.print("[bold]Available strategies:[/bold]")
        strategy_list = list(self.strategies.keys())

        for i, name in enumerate(strategy_list, 1):
            console.print(f"  {i}. {name}")

        console.print()
        choice = Prompt.ask("Select strategy number", default="1")

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(strategy_list):
                return strategy_list[idx]
            else:
                console.print("[red]Invalid selection[/red]")
                return None
        except ValueError:
            console.print("[red]Invalid input[/red]")
            return None

    def select_multiple_strategies(self) -> Optional[dict]:
        """Let user select multiple strategies."""
        if not self.strategies:
            console.print("[red]No strategies available![/red]")
            return None

        console.print("[bold]Available strategies:[/bold]")
        strategy_list = list(self.strategies.keys())

        for i, name in enumerate(strategy_list, 1):
            console.print(f"  {i}. {name}")

        console.print()
        console.print("[dim]Enter numbers separated by commas (e.g., 1,2,3) or 'all'[/dim]")
        choice = Prompt.ask("Select strategies", default="all")

        if choice.lower() == 'all':
            return self.strategies

        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            selected = {}
            for idx in indices:
                if 0 <= idx < len(strategy_list):
                    name = strategy_list[idx]
                    selected[name] = self.strategies[name]

            return selected if selected else None

        except ValueError:
            console.print("[red]Invalid input[/red]")
            return None

    def select_pair(self) -> Optional[str]:
        """Let user select a forex pair."""
        pairs_list = list(FOREX_PAIRS.keys())

        console.print("\n[bold]Popular forex pairs:[/bold]")
        console.print("  Majors: EURUSD, GBPUSD, USDJPY, AUDUSD, NZDUSD")
        console.print("  Volatile: GBPJPY, EURJPY, AUDJPY")
        console.print("  Exotics: USDTRY, USDZAR")
        console.print()

        pair = Prompt.ask("Enter pair", default="EURUSD")
        return pair.upper()

    def select_multiple_pairs(self) -> Optional[List[str]]:
        """Let user select multiple forex pairs."""
        console.print("\n[bold]Enter pairs separated by commas (e.g., EURUSD,GBPUSD,USDJPY)[/bold]")
        console.print("[dim]Or use presets: 'majors', 'volatile', 'all'[/dim]")
        console.print()

        choice = Prompt.ask("Select pairs", default="majors")

        if choice.lower() == 'majors':
            return ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'NZDUSD']
        elif choice.lower() == 'volatile':
            return ['GBPJPY', 'EURJPY', 'AUDJPY', 'NZDJPY']
        elif choice.lower() == 'all':
            return list(FOREX_PAIRS.keys())[:7]  # First 7 pairs
        else:
            pairs = [p.strip().upper() for p in choice.split(',')]
            return pairs

    def select_timeframe(self) -> str:
        """Let user select a timeframe."""
        console.print("\n[bold]Available timeframes:[/bold]")
        console.print("  [green]5m[/green]  - 5 Minutes  (up to 60 days)")
        console.print("  [green]15m[/green] - 15 Minutes (up to 60 days)")
        console.print("  [green]30m[/green] - 30 Minutes (up to 60 days)")
        console.print("  [green]1h[/green]  - 1 Hour     (up to 2 years)")
        console.print("  [green]4h[/green]  - 4 Hours    (up to 2 years)")
        console.print("  [green]1d[/green]  - 1 Day      (unlimited)")
        console.print()

        timeframe = Prompt.ask(
            "Select timeframe",
            choices=DEFAULT_TIMEFRAMES,
            default="1h"
        )

        # Show data limitation warning for intraday
        if timeframe in ['5m', '15m', '30m']:
            max_days = AVAILABLE_TIMEFRAMES[timeframe]['max_days']
            console.print(f"[yellow]⚠️  Note: {timeframe} data limited to {max_days} days by Yahoo Finance[/yellow]")

        return timeframe

    def get_date_range(self, timeframe: str = '1h') -> tuple[str, Optional[str]]:
        """Get date range from user, adjusted for timeframe limitations."""
        # Determine default date range based on timeframe
        max_days = AVAILABLE_TIMEFRAMES.get(timeframe, {}).get('max_days', 730)

        # Adjust default range if timeframe has limitations
        if timeframe in ['5m', '15m', '30m']:
            default_days = min(30, max_days)  # Use 30 days for intraday
            default_text = f"last {default_days} days"
        else:
            default_days = 730  # 2 years for hourly/daily
            default_text = "last 2 years"

        console.print()
        use_default = Confirm.ask(
            f"Use default date range? ({default_text})",
            default=True
        )

        if use_default:
            end = datetime.now().strftime('%Y-%m-%d')
            start = (datetime.now() - timedelta(days=default_days)).strftime('%Y-%m-%d')
        else:
            # Suggest appropriate start date based on timeframe
            if timeframe in ['5m', '15m', '30m']:
                suggested_start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            else:
                suggested_start = "2024-01-01"

            start = Prompt.ask("Start date (YYYY-MM-DD)", default=suggested_start)
            end = Prompt.ask("End date (YYYY-MM-DD)", default=datetime.now().strftime('%Y-%m-%d'))

        return start, end

    def display_results(self, stats, title: str):
        """Display backtest results in a nice format."""
        console.print(f"\n[bold cyan]═══ {title.upper()} ═══[/bold cyan]\n")

        # Create results table
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="yellow", no_wrap=True)
        table.add_column("Value", style="white", justify="right")

        # Performance metrics
        table.add_row("Total Return", f"{stats['Return [%]']:.2f}%")
        table.add_row("Buy & Hold Return", f"{stats.get('Buy & Hold Return [%]', 0):.2f}%")
        table.add_row("Sharpe Ratio", f"{stats.get('Sharpe Ratio', 0):.2f}")
        table.add_row("Max Drawdown", f"{stats['Max. Drawdown [%]']:.2f}%")
        table.add_row("", "")  # Spacer

        # Trading metrics
        table.add_row("Total Trades", f"{stats['# Trades']}")
        table.add_row("Win Rate", f"{stats.get('Win Rate [%]', 0):.1f}%")
        table.add_row("Profit Factor", f"{stats.get('Profit Factor', 0):.2f}")
        table.add_row("Avg Trade", f"{stats.get('Avg. Trade [%]', 0):.2f}%")

        console.print(table)
        console.print()

    def display_comparison(self, results: dict, title: str):
        """Display comparison table."""
        console.print(f"\n[bold cyan]═══ {title.upper()} ═══[/bold cyan]\n")

        analyzer = PerformanceAnalyzer()
        comparison = analyzer.compare(results, sort_by='sharpe_ratio')

        # Create comparison table
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
        table.add_column("Name", style="yellow", no_wrap=True)
        table.add_column("Return %", justify="right")
        table.add_column("Sharpe", justify="right")
        table.add_column("Max DD %", justify="right")
        table.add_column("Trades", justify="right")
        table.add_column("Win Rate %", justify="right")

        for name, row in comparison.iterrows():
            table.add_row(
                name,
                f"{row['total_return']:.2f}",
                f"{row['sharpe_ratio']:.2f}",
                f"{row['max_drawdown']:.2f}",
                f"{int(row['total_trades'])}",
                f"{row['win_rate']:.1f}"
            )

        console.print(table)
        console.print()


def main():
    """Main entry point."""
    manager = StrategyManager()
    manager.run()


if __name__ == '__main__':
    main()