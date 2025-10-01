"""
Test script to verify timeframe and realistic spread functionality
"""

from backtester import ForexBacktester
from strategies.ma_crossover import MACrossover
from forex_config import print_spread_table, get_spread, format_spread_pips
from datetime import datetime, timedelta

print("="*80)
print("  TESTING REALISTIC SPREADS AND TIMEFRAME SUPPORT")
print("="*80)

# Test 1: Display spread table
print("\n1. Testing spread configuration...")
print_spread_table()

# Test 2: Test specific spreads
print("\n2. Testing spread calculations...")
test_cases = [
    ('EURUSD', '5m'),
    ('EURUSD', '1h'),
    ('GBPJPY', '15m'),
    ('USDTRY', '1h'),
]

for pair, timeframe in test_cases:
    spread = get_spread(pair, timeframe)
    formatted = format_spread_pips(spread, pair)
    print(f"  {pair} {timeframe}: {formatted} ({spread:.6f})")

# Test 3: Run a quick backtest on different timeframes
print("\n3. Testing backtester with different timeframes...")

backtester = ForexBacktester()

# Test on 1h (should have longer history available)
print("\n" + "-"*80)
print("Testing EURUSD on 1h timeframe")
print("-"*80)

end = datetime.now().strftime('%Y-%m-%d')
start = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')

try:
    stats = backtester.run(
        strategy=MACrossover,
        pair='EURUSD',
        timeframe='1h',
        start=start,
        end=end,
        show_plot=False
    )

    print(f"\n✅ 1h backtest completed successfully!")
    print(f"   Return: {stats['Return [%]']:.2f}%")
    print(f"   Trades: {stats['# Trades']}")
    print(f"   Sharpe: {stats['Sharpe Ratio']:.2f}")

except Exception as e:
    print(f"❌ Error: {e}")

# Test on 15m (limited history)
print("\n" + "-"*80)
print("Testing EURUSD on 15m timeframe")
print("-"*80)

end = datetime.now().strftime('%Y-%m-%d')
start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

try:
    stats = backtester.run(
        strategy=MACrossover,
        pair='EURUSD',
        timeframe='15m',
        start=start,
        end=end,
        show_plot=False
    )

    print(f"\n✅ 15m backtest completed successfully!")
    print(f"   Return: {stats['Return [%]']:.2f}%")
    print(f"   Trades: {stats['# Trades']}")
    print(f"   Sharpe: {stats['Sharpe Ratio']:.2f}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
print("  TEST COMPLETE!")
print("="*80)
