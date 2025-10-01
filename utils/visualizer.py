"""
Visualization Utilities

Enhanced charting and visualization for backtest results.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
import numpy as np


# Set style for better-looking plots
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (14, 8)


class Visualizer:
    """
    Create visualizations for backtest results.

    Usage:
    ------
    viz = Visualizer()

    # Plot equity curves
    viz.plot_equity_curves({'Strategy A': equity1, 'Strategy B': equity2})

    # Plot drawdown
    viz.plot_drawdown(equity_curve)

    # Plot monthly returns heatmap
    viz.plot_monthly_returns(returns)
    """

    @staticmethod
    def plot_equity_curves(equity_curves: Dict[str, pd.Series],
                          title: str = "Strategy Comparison - Equity Curves",
                          save_path: Optional[str] = None):
        """
        Plot equity curves for multiple strategies.

        Parameters:
        -----------
        equity_curves : dict
            Dictionary mapping strategy names to equity curves
        title : str
            Plot title
        save_path : str, optional
            Path to save the plot
        """
        plt.figure(figsize=(14, 7))

        for name, equity in equity_curves.items():
            # Normalize to start at 100
            normalized = (equity / equity.iloc[0]) * 100
            plt.plot(normalized.index, normalized.values, label=name, linewidth=2)

        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Equity (Base = 100)', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Saved plot to {save_path}")

        plt.show()

    @staticmethod
    def plot_drawdown(equity_curve: pd.Series,
                     title: str = "Drawdown Over Time",
                     save_path: Optional[str] = None):
        """
        Plot underwater/drawdown chart.

        Parameters:
        -----------
        equity_curve : pd.Series
            Equity curve over time
        title : str
            Plot title
        save_path : str, optional
            Path to save the plot
        """
        # Calculate drawdown
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max * 100

        plt.figure(figsize=(14, 5))
        plt.fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
        plt.plot(drawdown.index, drawdown.values, color='red', linewidth=1)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Drawdown (%)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Saved plot to {save_path}")

        plt.show()

    @staticmethod
    def plot_monthly_returns(returns: pd.Series,
                           title: str = "Monthly Returns Heatmap",
                           save_path: Optional[str] = None):
        """
        Plot monthly returns as a heatmap.

        Parameters:
        -----------
        returns : pd.Series
            Daily returns series
        title : str
            Plot title
        save_path : str, optional
            Path to save the plot
        """
        # Resample to monthly returns
        monthly = returns.resample('M').apply(lambda x: (1 + x).prod() - 1) * 100

        # Create year/month pivot table
        monthly_df = pd.DataFrame({
            'Year': monthly.index.year,
            'Month': monthly.index.month,
            'Return': monthly.values
        })

        pivot = monthly_df.pivot(index='Month', columns='Year', values='Return')

        # Plot heatmap
        plt.figure(figsize=(12, 6))
        sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn', center=0,
                   cbar_kws={'label': 'Return (%)'}, linewidths=0.5)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.ylabel('Month', fontsize=12)
        plt.xlabel('Year', fontsize=12)

        # Set month names
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        plt.yticks(np.arange(12) + 0.5, month_names, rotation=0)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Saved plot to {save_path}")

        plt.show()

    @staticmethod
    def plot_returns_distribution(returns: pd.Series,
                                 title: str = "Returns Distribution",
                                 save_path: Optional[str] = None):
        """
        Plot distribution of returns.

        Parameters:
        -----------
        returns : pd.Series
            Returns series
        title : str
            Plot title
        save_path : str, optional
            Path to save the plot
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Histogram
        ax1.hist(returns * 100, bins=50, alpha=0.7, color='blue', edgecolor='black')
        ax1.axvline(returns.mean() * 100, color='red', linestyle='--',
                   linewidth=2, label=f'Mean: {returns.mean()*100:.2f}%')
        ax1.set_title('Returns Histogram', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Return (%)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Q-Q plot
        from scipy import stats
        stats.probplot(returns, dist="norm", plot=ax2)
        ax2.set_title('Q-Q Plot (Normal Distribution)', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        fig.suptitle(title, fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Saved plot to {save_path}")

        plt.show()

    @staticmethod
    def plot_trade_analysis(trades_df: pd.DataFrame,
                          title: str = "Trade Analysis",
                          save_path: Optional[str] = None):
        """
        Plot trade-by-trade analysis.

        Parameters:
        -----------
        trades_df : pd.DataFrame
            DataFrame of trades from backtest
        title : str
            Plot title
        save_path : str, optional
            Path to save the plot
        """
        if trades_df is None or len(trades_df) == 0:
            print("No trades to plot")
            return

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Cumulative PnL
        cumulative_pnl = trades_df['PnL'].cumsum()
        ax1.plot(cumulative_pnl, linewidth=2, color='blue')
        ax1.set_title('Cumulative PnL', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Trade Number')
        ax1.set_ylabel('Cumulative PnL')
        ax1.grid(True, alpha=0.3)

        # 2. Individual Trade PnL
        colors = ['green' if x > 0 else 'red' for x in trades_df['PnL']]
        ax2.bar(range(len(trades_df)), trades_df['PnL'], color=colors, alpha=0.6)
        ax2.set_title('Individual Trade PnL', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Trade Number')
        ax2.set_ylabel('PnL')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.grid(True, alpha=0.3)

        # 3. Trade Duration Distribution
        if 'Duration' in trades_df.columns:
            durations = trades_df['Duration'].dt.total_seconds() / 3600  # Convert to hours
            ax3.hist(durations, bins=30, alpha=0.7, color='purple', edgecolor='black')
            ax3.set_title('Trade Duration Distribution', fontsize=12, fontweight='bold')
            ax3.set_xlabel('Duration (hours)')
            ax3.set_ylabel('Frequency')
            ax3.grid(True, alpha=0.3)

        # 4. Win/Loss Ratio
        wins = len(trades_df[trades_df['PnL'] > 0])
        losses = len(trades_df[trades_df['PnL'] < 0])
        ax4.pie([wins, losses], labels=['Wins', 'Losses'],
               autopct='%1.1f%%', colors=['green', 'red'], startangle=90)
        ax4.set_title('Win/Loss Ratio', fontsize=12, fontweight='bold')

        fig.suptitle(title, fontsize=16, fontweight='bold', y=1.00)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Saved plot to {save_path}")

        plt.show()

    @staticmethod
    def create_tearsheet(stats: pd.Series,
                        equity_curve: pd.Series,
                        returns: pd.Series,
                        trades_df: Optional[pd.DataFrame] = None,
                        strategy_name: str = "Strategy",
                        save_path: Optional[str] = None):
        """
        Create a comprehensive tearsheet with multiple charts.

        Parameters:
        -----------
        stats : pd.Series
            Backtest statistics
        equity_curve : pd.Series
            Equity curve over time
        returns : pd.Series
            Returns series
        trades_df : pd.DataFrame, optional
            DataFrame of trades
        strategy_name : str
            Name of the strategy
        save_path : str, optional
            Path to save the tearsheet
        """
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(4, 2, hspace=0.3, wspace=0.3)

        # 1. Equity Curve
        ax1 = fig.add_subplot(gs[0, :])
        normalized = (equity_curve / equity_curve.iloc[0]) * 100
        ax1.plot(normalized.index, normalized.values, linewidth=2, color='blue')
        ax1.set_title('Equity Curve', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Equity (Base = 100)')
        ax1.grid(True, alpha=0.3)

        # 2. Drawdown
        ax2 = fig.add_subplot(gs[1, :])
        running_max = equity_curve.expanding().max()
        drawdown = (equity_curve - running_max) / running_max * 100
        ax2.fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
        ax2.plot(drawdown.index, drawdown.values, color='red', linewidth=1)
        ax2.set_title('Drawdown', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Drawdown (%)')
        ax2.grid(True, alpha=0.3)

        # 3. Returns Distribution
        ax3 = fig.add_subplot(gs[2, 0])
        ax3.hist(returns * 100, bins=50, alpha=0.7, color='blue', edgecolor='black')
        ax3.axvline(returns.mean() * 100, color='red', linestyle='--', linewidth=2)
        ax3.set_title('Returns Distribution', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Return (%)')
        ax3.set_ylabel('Frequency')
        ax3.grid(True, alpha=0.3)

        # 4. Monthly Returns
        ax4 = fig.add_subplot(gs[2, 1])
        monthly = returns.resample('M').apply(lambda x: (1 + x).prod() - 1) * 100
        colors = ['green' if x > 0 else 'red' for x in monthly]
        ax4.bar(monthly.index, monthly.values, color=colors, alpha=0.6, width=20)
        ax4.set_title('Monthly Returns', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Return (%)')
        ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax4.grid(True, alpha=0.3)

        # 5. Key Metrics Table
        ax5 = fig.add_subplot(gs[3, :])
        ax5.axis('tight')
        ax5.axis('off')

        metrics_data = [
            ['Total Return', f"{stats['Return [%]']:.2f}%"],
            ['Sharpe Ratio', f"{stats.get('Sharpe Ratio', 0):.2f}"],
            ['Max Drawdown', f"{stats['Max. Drawdown [%]']:.2f}%"],
            ['Win Rate', f"{stats.get('Win Rate [%]', 0):.1f}%"],
            ['Total Trades', f"{stats['# Trades']}"],
            ['Profit Factor', f"{stats.get('Profit Factor', 0):.2f}"],
        ]

        table = ax5.table(cellText=metrics_data, colLabels=['Metric', 'Value'],
                         cellLoc='left', loc='center',
                         colWidths=[0.3, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)

        fig.suptitle(f'{strategy_name} - Performance Tearsheet',
                    fontsize=16, fontweight='bold')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Saved tearsheet to {save_path}")

        plt.show()