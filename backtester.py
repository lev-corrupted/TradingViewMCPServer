"""
Main Backtesting Engine

Simplified interface for running backtests on forex strategies.
"""

from backtesting import Backtest
from typing import Dict, Optional, Type, Union
import pandas as pd
from pathlib import Path

from strategies.base_strategy import BaseStrategy
from utils.data_loader import DataLoader
from utils.performance import PerformanceAnalyzer, print_summary
from forex_config import get_spread, get_margin_requirement, format_spread_pips


class ForexBacktester:
    """
    Main backtesting engine for forex strategies.

    Usage:
    ------
    from backtester import ForexBacktester
    from strategies.ma_crossover import MACrossover

    backtester = ForexBacktester()
    results = backtester.run(
        strategy=MACrossover,
        pair='EURUSD',
        start='2023-01-01',
        end='2024-01-01'
    )
    """

    def __init__(self,
                 cash: float = 10000,
                 commission: Optional[float] = None,
                 margin: Optional[float] = None,
                 exclusive_orders: bool = True,
                 use_realistic_spreads: bool = True):
        """
        Initialize backtester with default settings.

        Parameters:
        -----------
        cash : float
            Initial capital (default: $10,000)
        commission : float, optional
            Commission per trade as decimal. If None, auto-calculated based on pair and timeframe.
        margin : float, optional
            Margin requirement. If None, auto-calculated based on pair type.
        exclusive_orders : bool
            If True, only one order can be active at a time
        use_realistic_spreads : bool
            If True, automatically use realistic spreads based on pair and timeframe (default: True)
        """
        self.cash = cash
        self.commission = commission
        self.margin = margin
        self.exclusive_orders = exclusive_orders
        self.use_realistic_spreads = use_realistic_spreads
        self.data_loader = DataLoader()

    def run(self,
            strategy: Type[BaseStrategy],
            pair: Optional[str] = None,
            data: Optional[pd.DataFrame] = None,
            start: Optional[str] = None,
            end: Optional[str] = None,
            timeframe: str = '1h',
            optimize: bool = False,
            optimize_params: Optional[Dict] = None,
            show_plot: bool = False,
            **strategy_kwargs) -> pd.Series:
        """
        Run a backtest on a strategy.

        Parameters:
        -----------
        strategy : class
            Strategy class (must inherit from BaseStrategy)
        pair : str, optional
            Forex pair to test (e.g., 'EURUSD'). Required if data not provided.
        data : pd.DataFrame, optional
            Custom data to test on. If not provided, will download pair data.
        start : str, optional
            Start date (YYYY-MM-DD)
        end : str, optional
            End date (YYYY-MM-DD)
        timeframe : str, optional
            Timeframe for data (default: '1h'). Options: '5m', '15m', '30m', '1h', '4h', '1d'
        optimize : bool, optional
            If True, run parameter optimization
        optimize_params : dict, optional
            Parameters to optimize. Format: {'param_name': range(10, 50, 5)}
        show_plot : bool, optional
            If True, show interactive plot
        **strategy_kwargs : dict
            Additional parameters to pass to strategy

        Returns:
        --------
        pd.Series
            Backtest statistics

        Example:
        --------
        # Simple backtest
        results = backtester.run(MACrossover, pair='EURUSD', start='2023-01-01')

        # With specific timeframe
        results = backtester.run(
            MACrossover,
            pair='EURUSD',
            timeframe='15m',
            start='2024-01-01'
        )

        # With custom parameters
        results = backtester.run(
            MACrossover,
            pair='EURUSD',
            timeframe='1h',
            fast_period=15,
            slow_period=40
        )

        # With optimization
        results = backtester.run(
            MACrossover,
            pair='EURUSD',
            timeframe='1h',
            optimize=True,
            optimize_params={
                'fast_period': range(5, 20, 5),
                'slow_period': range(20, 50, 5)
            }
        )
        """
        # Load data
        if data is None:
            if pair is None:
                raise ValueError("Must provide either 'pair' or 'data'")
            print(f"📊 Loading data for {pair} ({timeframe})...")
            data = self.data_loader.load(pair, start, end, interval=timeframe)
            print(f"✅ Loaded {len(data)} bars")

        # Calculate realistic spread/commission if enabled
        commission = self.commission
        margin = self.margin

        if self.use_realistic_spreads and pair is not None:
            # Auto-calculate spread based on pair and timeframe
            if commission is None:
                commission = get_spread(pair, timeframe)
                spread_pips = format_spread_pips(commission, pair)
                print(f"💰 Using realistic spread: {spread_pips} ({commission:.6f})")

            # Auto-calculate margin based on pair type
            if margin is None:
                margin = get_margin_requirement(pair)
                leverage = 1 / margin
                print(f"📊 Using margin: {margin:.2%} (Leverage: {leverage:.0f}:1)")

        # Set default values if still None
        if commission is None:
            commission = 0.0002  # Fallback: 2 pips
        if margin is None:
            margin = 1.0  # Fallback: No leverage

        # Set strategy parameters if provided
        if strategy_kwargs:
            # Create a modified strategy class with custom parameters
            class CustomStrategy(strategy):
                pass

            for key, value in strategy_kwargs.items():
                setattr(CustomStrategy, key, value)

            strategy = CustomStrategy

        # Create backtest
        bt = Backtest(
            data,
            strategy,
            cash=self.cash,
            commission=commission,
            margin=margin,
            exclusive_orders=self.exclusive_orders
        )

        # Run backtest
        if optimize and optimize_params:
            print(f"🔧 Optimizing parameters...")
            stats = bt.optimize(**optimize_params)
            print(f"✅ Optimization complete!")
            print(f"📈 Best parameters: {stats._strategy}")
        else:
            print(f"🚀 Running backtest...")
            stats = bt.run()
            print(f"✅ Backtest complete!")

        # Show plot if requested
        if show_plot:
            bt.plot()

        return stats

    def run_multiple(self,
                    strategies: Dict[str, Type[BaseStrategy]],
                    pair: str,
                    start: Optional[str] = None,
                    end: Optional[str] = None,
                    timeframe: str = '1h',
                    compare: bool = True) -> Dict[str, pd.Series]:
        """
        Run multiple strategies on the same data.

        Parameters:
        -----------
        strategies : dict
            Dictionary mapping strategy names to strategy classes
        pair : str
            Forex pair to test
        start : str, optional
            Start date
        end : str, optional
            End date
        timeframe : str, optional
            Timeframe (default: '1h')
        compare : bool, optional
            If True, print comparison table

        Returns:
        --------
        dict
            Dictionary mapping strategy names to results

        Example:
        --------
        from strategies.ma_crossover import MACrossover
        from strategies.rsi_strategy import RSIStrategy

        results = backtester.run_multiple(
            strategies={
                'MA Crossover': MACrossover,
                'RSI Strategy': RSIStrategy
            },
            pair='EURUSD',
            timeframe='15m',
            start='2024-01-01'
        )
        """
        # Load data once
        print(f"📊 Loading data for {pair} ({timeframe})...")
        data = self.data_loader.load(pair, start, end, interval=timeframe)
        print(f"✅ Loaded {len(data)} bars\n")

        results = {}

        # Run each strategy
        for name, strategy in strategies.items():
            print(f"🚀 Running {name}...")
            results[name] = self.run(
                strategy=strategy,
                pair=pair,
                data=data,
                timeframe=timeframe,
                show_plot=False
            )
            print()

        # Compare results
        if compare:
            print("\n" + "="*80)
            print(f"  STRATEGY COMPARISON - {pair}")
            print("="*80 + "\n")

            analyzer = PerformanceAnalyzer()
            comparison = analyzer.compare(results, sort_by='sharpe_ratio')

            # Print comparison table
            print(comparison.to_string())
            print("\n")

        return results

    def run_on_multiple_pairs(self,
                             strategy: Type[BaseStrategy],
                             pairs: list[str],
                             start: Optional[str] = None,
                             end: Optional[str] = None,
                             timeframe: str = '1h',
                             compare: bool = True,
                             **strategy_kwargs) -> Dict[str, pd.Series]:
        """
        Run a single strategy on multiple forex pairs.

        Parameters:
        -----------
        strategy : class
            Strategy class to test
        pairs : list[str]
            List of forex pairs to test
        start : str, optional
            Start date
        end : str, optional
            End date
        timeframe : str, optional
            Timeframe (default: '1h')
        compare : bool, optional
            If True, print comparison table
        **strategy_kwargs : dict
            Parameters for the strategy

        Returns:
        --------
        dict
            Dictionary mapping pair names to results

        Example:
        --------
        results = backtester.run_on_multiple_pairs(
            strategy=MACrossover,
            pairs=['EURUSD', 'GBPUSD', 'USDJPY'],
            timeframe='15m',
            start='2024-01-01'
        )
        """
        results = {}

        for pair in pairs:
            print(f"\n{'='*60}")
            print(f"  Testing {strategy.__name__} on {pair} ({timeframe})")
            print(f"{'='*60}\n")

            try:
                results[pair] = self.run(
                    strategy=strategy,
                    pair=pair,
                    start=start,
                    end=end,
                    timeframe=timeframe,
                    show_plot=False,
                    **strategy_kwargs
                )
            except Exception as e:
                print(f"❌ Error testing {pair}: {e}\n")
                continue

        # Compare results
        if compare and len(results) > 0:
            print("\n" + "="*80)
            print(f"  PAIR COMPARISON - {strategy.__name__}")
            print("="*80 + "\n")

            analyzer = PerformanceAnalyzer()
            comparison = analyzer.compare(results, sort_by='sharpe_ratio')
            print(comparison.to_string())
            print("\n")

        return results


# ===== CONVENIENCE FUNCTION =====

def quick_backtest(strategy,
                  pair: str = 'EURUSD',
                  start: str = '2024-01-01',
                  end: Optional[str] = None,
                  timeframe: str = '1h',
                  show_plot: bool = True,
                  **kwargs):
    """
    Quick one-line backtest function.

    Example:
    --------
    from backtester import quick_backtest
    from strategies.ma_crossover import MACrossover

    # Quick test with defaults
    quick_backtest(MACrossover, pair='EURUSD', show_plot=True)

    # With specific timeframe
    quick_backtest(MACrossover, pair='EURUSD', timeframe='15m', start='2024-01-01')
    """
    backtester = ForexBacktester()
    stats = backtester.run(
        strategy=strategy,
        pair=pair,
        start=start,
        end=end,
        timeframe=timeframe,
        show_plot=show_plot,
        **kwargs
    )

    # Print summary
    print_summary(stats, strategy_name=strategy.__name__)

    return stats


# ===== CLI INTERFACE =====

if __name__ == '__main__':
    import argparse
    from strategies import discover_strategies

    parser = argparse.ArgumentParser(description='Run forex backtest')
    parser.add_argument('strategy', type=str, help='Strategy name')
    parser.add_argument('--pair', type=str, default='EURUSD', help='Forex pair')
    parser.add_argument('--start', type=str, default='2023-01-01', help='Start date')
    parser.add_argument('--end', type=str, default=None, help='End date')
    parser.add_argument('--plot', action='store_true', help='Show plot')
    parser.add_argument('--list', action='store_true', help='List available strategies')

    args = parser.parse_args()

    # Discover strategies
    strategies = discover_strategies()

    if args.list:
        print("\nAvailable strategies:")
        for name in strategies.keys():
            print(f"  - {name}")
        exit(0)

    # Find strategy
    strategy_class = strategies.get(args.strategy)
    if strategy_class is None:
        print(f"❌ Strategy '{args.strategy}' not found")
        print(f"Available strategies: {list(strategies.keys())}")
        exit(1)

    # Run backtest
    quick_backtest(
        strategy_class,
        pair=args.pair,
        start=args.start,
        end=args.end,
        show_plot=args.plot
    )