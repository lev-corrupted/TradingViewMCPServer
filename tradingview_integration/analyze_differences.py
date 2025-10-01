#!/usr/bin/env python3
"""Analyze differences between TradingView and Python backtests"""

def compare_results():
    """
    Manual comparison helper
    """
    print("="*70)
    print("BACKTEST COMPARISON TOOL")
    print("="*70)

    print("\nEnter your results:\n")

    # Python results
    print("PYTHON BACKTEST:")
    py_return = float(input("  Return %: "))
    py_trades = int(input("  Total Trades: "))
    py_winrate = float(input("  Win Rate %: "))
    py_sharpe = float(input("  Sharpe Ratio: "))

    # TradingView results
    print("\nTRADINGVIEW BACKTEST:")
    tv_return = float(input("  Return %: "))
    tv_trades = int(input("  Total Trades: "))
    tv_winrate = float(input("  Win Rate %: "))

    # Analysis
    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)

    return_diff = abs(py_return - tv_return)
    trades_diff = abs(py_trades - tv_trades)
    winrate_diff = abs(py_winrate - tv_winrate)

    print(f"\nReturn Difference: {return_diff:.2f}%")
    print(f"Trade Count Difference: {trades_diff}")
    print(f"Win Rate Difference: {winrate_diff:.2f}%")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)

    if return_diff < 2 and trades_diff < 5:
        print("✅ EXCELLENT: Results match closely!")
        print("   Your Python backtesting system is accurate.")
    elif return_diff < 5 and trades_diff < 10:
        print("⚠️  ACCEPTABLE: Minor differences detected")
        print("   Likely due to commission/spread modeling differences")
    else:
        print("❌ SIGNIFICANT DIFFERENCES FOUND")
        print("   Possible causes:")
        print("   - Different data sources")
        print("   - Different commission models")
        print("   - Different execution logic")
        print("   - Data alignment issues")

if __name__ == "__main__":
    compare_results()
