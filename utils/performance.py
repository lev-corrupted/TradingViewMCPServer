"""
Performance Analysis Utilities

Tools for analyzing and comparing strategy performance.
"""

import pandas as pd
import numpy as np
from typing import Union, List, Dict
from datetime import datetime


class PerformanceAnalyzer:
    """
    Analyze and compare backtest results.

    Usage:
    ------
    analyzer = PerformanceAnalyzer()

    # Analyze single strategy
    metrics = analyzer.analyze(stats)

    # Compare multiple strategies
    comparison = analyzer.compare({
        'MA Crossover': stats1,
        'RSI Strategy': stats2,
        'MACD': stats3
    })
    """

    @staticmethod
    def analyze(stats: pd.Series) -> Dict:
        """
        Extract and calculate key performance metrics.

        Parameters:
        -----------
        stats : pd.Series
            Backtest results from bt.run()

        Returns:
        --------
        dict
            Dictionary of performance metrics
        """
        metrics = {
            'total_return': stats.get('Return [%]', 0),
            'buy_hold_return': stats.get('Buy & Hold Return [%]', 0),
            'total_trades': stats.get('# Trades', 0),
            'win_rate': stats.get('Win Rate [%]', 0),
            'sharpe_ratio': stats.get('Sharpe Ratio', 0),
            'sortino_ratio': stats.get('Sortino Ratio', 0),
            'calmar_ratio': stats.get('Calmar Ratio', 0),
            'max_drawdown': stats.get('Max. Drawdown [%]', 0),
            'avg_drawdown': stats.get('Avg. Drawdown [%]', 0),
            'max_drawdown_duration': stats.get('Max. Drawdown Duration', 0),
            'avg_trade': stats.get('Avg. Trade [%]', 0),
            'avg_win': stats.get('Avg. Win [%]', 0),
            'avg_loss': stats.get('Avg. Loss [%]', 0),
            'profit_factor': stats.get('Profit Factor', 0),
            'expectancy': stats.get('Expectancy [%]', 0),
            'exposure_time': stats.get('Exposure Time [%]', 0),
        }

        # Calculate additional metrics
        if metrics['total_trades'] > 0:
            metrics['avg_trades_per_month'] = PerformanceAnalyzer._calculate_trades_per_month(stats)
            metrics['risk_reward_ratio'] = abs(metrics['avg_win'] / metrics['avg_loss']) if metrics['avg_loss'] != 0 else 0

        return metrics

    @staticmethod
    def compare(results: Dict[str, pd.Series],
                sort_by: str = 'sharpe_ratio',
                ascending: bool = False) -> pd.DataFrame:
        """
        Compare multiple strategy results.

        Parameters:
        -----------
        results : dict
            Dictionary mapping strategy names to backtest stats
        sort_by : str, optional
            Metric to sort by. Default is 'sharpe_ratio'.
        ascending : bool, optional
            Sort order. Default is False (descending).

        Returns:
        --------
        pd.DataFrame
            Comparison table of all strategies
        """
        comparison = {}

        for name, stats in results.items():
            metrics = PerformanceAnalyzer.analyze(stats)
            comparison[name] = metrics

        df = pd.DataFrame(comparison).T

        # Sort by specified metric
        if sort_by in df.columns:
            df = df.sort_values(by=sort_by, ascending=ascending)

        return df

    @staticmethod
    def rank_strategies(results: Dict[str, pd.Series],
                        weights: Dict[str, float] = None) -> pd.DataFrame:
        """
        Rank strategies using a weighted scoring system.

        Parameters:
        -----------
        results : dict
            Dictionary mapping strategy names to backtest stats
        weights : dict, optional
            Custom weights for each metric. Higher weight = more important.
            Default weights favor risk-adjusted returns.

        Returns:
        --------
        pd.DataFrame
            Ranked strategies with scores
        """
        if weights is None:
            # Default weights
            weights = {
                'sharpe_ratio': 0.30,      # Risk-adjusted return
                'total_return': 0.20,      # Raw return
                'win_rate': 0.15,          # Consistency
                'profit_factor': 0.15,     # Win/loss ratio
                'max_drawdown': 0.10,      # Risk (inverse)
                'total_trades': 0.10,      # Activity
            }

        comparison_df = PerformanceAnalyzer.compare(results)

        # Normalize metrics to 0-1 scale
        scores = pd.DataFrame(index=comparison_df.index)

        for metric, weight in weights.items():
            if metric in comparison_df.columns:
                col = comparison_df[metric]

                # For metrics where lower is better (drawdown), invert
                if metric in ['max_drawdown', 'avg_drawdown']:
                    normalized = 1 - (col - col.min()) / (col.max() - col.min() + 1e-9)
                else:
                    normalized = (col - col.min()) / (col.max() - col.min() + 1e-9)

                scores[metric] = normalized * weight

        # Calculate total score
        scores['total_score'] = scores.sum(axis=1)

        # Merge with original metrics
        result = comparison_df.copy()
        result['score'] = scores['total_score']
        result = result.sort_values('score', ascending=False)

        return result

    @staticmethod
    def calculate_custom_metrics(stats: pd.Series, equity_curve: pd.Series = None) -> Dict:
        """
        Calculate additional custom metrics not provided by backtesting.py.

        Parameters:
        -----------
        stats : pd.Series
            Backtest results
        equity_curve : pd.Series, optional
            Equity curve over time

        Returns:
        --------
        dict
            Custom metrics
        """
        metrics = {}

        if equity_curve is not None and len(equity_curve) > 0:
            # Underwater curve (drawdown over time)
            running_max = equity_curve.expanding().max()
            underwater = (equity_curve - running_max) / running_max

            # Recovery time
            metrics['avg_recovery_days'] = PerformanceAnalyzer._calculate_avg_recovery(underwater)

            # Consecutive wins/losses
            trades = stats.get('_trades', None)
            if trades is not None and len(trades) > 0:
                pnl = trades['PnL']
                metrics['max_consecutive_wins'] = PerformanceAnalyzer._max_consecutive(pnl > 0)
                metrics['max_consecutive_losses'] = PerformanceAnalyzer._max_consecutive(pnl < 0)

        return metrics

    @staticmethod
    def _calculate_trades_per_month(stats: pd.Series) -> float:
        """Calculate average number of trades per month."""
        total_trades = stats.get('# Trades', 0)
        duration = stats.get('Duration', None)

        if duration and total_trades > 0:
            # Convert duration to months (approximate)
            days = duration.days
            months = days / 30.0
            return total_trades / months if months > 0 else 0

        return 0

    @staticmethod
    def _calculate_avg_recovery(underwater: pd.Series) -> float:
        """Calculate average time to recover from drawdowns."""
        # Find drawdown periods
        in_drawdown = underwater < 0
        drawdown_periods = in_drawdown.astype(int).diff().fillna(0)

        starts = drawdown_periods[drawdown_periods == 1].index
        ends = drawdown_periods[drawdown_periods == -1].index

        if len(starts) == 0 or len(ends) == 0:
            return 0

        # Calculate recovery times
        recovery_times = []
        for start in starts:
            # Find next end after this start
            matching_ends = ends[ends > start]
            if len(matching_ends) > 0:
                end = matching_ends[0]
                recovery_times.append((end - start).days)

        return np.mean(recovery_times) if recovery_times else 0

    @staticmethod
    def _max_consecutive(series: pd.Series) -> int:
        """Find maximum consecutive True values."""
        if len(series) == 0:
            return 0

        max_count = 0
        current_count = 0

        for val in series:
            if val:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0

        return max_count


def print_summary(stats: pd.Series, strategy_name: str = "Strategy"):
    """
    Print a clean summary of backtest results.

    Parameters:
    -----------
    stats : pd.Series
        Backtest results
    strategy_name : str
        Name of the strategy
    """
    print(f"\n{'='*60}")
    print(f"  {strategy_name} - Backtest Results")
    print(f"{'='*60}\n")

    # Performance
    print("📊 PERFORMANCE")
    print(f"  Total Return:        {stats['Return [%]']:>8.2f}%")
    print(f"  Buy & Hold Return:   {stats.get('Buy & Hold Return [%]', 0):>8.2f}%")
    print(f"  Sharpe Ratio:        {stats.get('Sharpe Ratio', 0):>8.2f}")
    print(f"  Sortino Ratio:       {stats.get('Sortino Ratio', 0):>8.2f}")
    print(f"  Calmar Ratio:        {stats.get('Calmar Ratio', 0):>8.2f}")

    # Risk
    print(f"\n⚠️  RISK")
    print(f"  Max Drawdown:        {stats['Max. Drawdown [%]']:>8.2f}%")
    print(f"  Avg Drawdown:        {stats.get('Avg. Drawdown [%]', 0):>8.2f}%")
    print(f"  Exposure Time:       {stats.get('Exposure Time [%]', 0):>8.2f}%")

    # Trading
    print(f"\n💰 TRADING")
    print(f"  Total Trades:        {stats['# Trades']:>8}")
    print(f"  Win Rate:            {stats.get('Win Rate [%]', 0):>8.1f}%")
    print(f"  Avg Trade:           {stats.get('Avg. Trade [%]', 0):>8.2f}%")
    print(f"  Best Trade:          {stats.get('Best Trade [%]', 0):>8.2f}%")
    print(f"  Worst Trade:         {stats.get('Worst Trade [%]', 0):>8.2f}%")
    print(f"  Profit Factor:       {stats.get('Profit Factor', 0):>8.2f}")

    print(f"\n{'='*60}\n")