"""
Forex Trading Configuration

Realistic trading costs and constraints for forex pairs.
Based on typical retail broker spreads and market conditions.
"""

# ===== REALISTIC SPREADS =====
# Spreads in decimal format (e.g., 0.00020 = 2.0 pips for EUR/USD)
# These represent typical retail broker spreads during normal market hours

PAIR_SPREADS = {
    # MAJORS (Tightest spreads - most liquid)
    'EURUSD': 0.00010,   # 1.0 pips (0.1 basis points)
    'GBPUSD': 0.00015,   # 1.5 pips
    'USDJPY': 0.010,     # 1.0 pips (JPY pairs: 1 pip = 0.01)
    'USDCHF': 0.00015,   # 1.5 pips
    'AUDUSD': 0.00012,   # 1.2 pips
    'USDCAD': 0.00015,   # 1.5 pips
    'NZDUSD': 0.00020,   # 2.0 pips

    # CROSSES (Wider spreads - medium liquidity)
    'GBPJPY': 0.025,     # 2.5 pips
    'EURJPY': 0.020,     # 2.0 pips
    'AUDJPY': 0.025,     # 2.5 pips
    'NZDJPY': 0.030,     # 3.0 pips
    'EURGBP': 0.00015,   # 1.5 pips
    'EURAUD': 0.00025,   # 2.5 pips
    'EURCHF': 0.00020,   # 2.0 pips
    'GBPAUD': 0.00035,   # 3.5 pips
    'GBPCAD': 0.00040,   # 4.0 pips
    'AUDCAD': 0.00025,   # 2.5 pips

    # EXOTICS (Very wide spreads - low liquidity)
    'USDTRY': 0.0100,    # 100+ pips (extremely volatile)
    'USDZAR': 0.0150,    # 150+ pips
    'USDMXN': 0.0080,    # 80+ pips
    'USDBRL': 0.0120,    # 120+ pips
}

# ===== TIMEFRAME SPREAD MULTIPLIERS =====
# Lower timeframes have wider spreads due to:
# - More frequent trading = more spread costs
# - Lower liquidity on some platforms
# - Increased slippage probability

TIMEFRAME_SPREAD_MULTIPLIERS = {
    '1m': 1.8,    # 80% wider spread
    '5m': 1.5,    # 50% wider spread
    '15m': 1.3,   # 30% wider spread
    '30m': 1.2,   # 20% wider spread
    '1h': 1.1,    # 10% wider spread
    '2h': 1.0,    # Normal spread
    '4h': 0.95,   # 5% tighter spread
    '1d': 0.9,    # 10% tighter spread (best execution)
    '1wk': 0.85,  # 15% tighter spread
}

# ===== AVAILABLE TIMEFRAMES =====
# Supported timeframes for backtesting
# Note: yfinance has data limitations on lower timeframes (usually max 60 days for intraday)

AVAILABLE_TIMEFRAMES = {
    '1m': {'name': '1 Minute', 'yf_interval': '1m', 'max_days': 7},
    '5m': {'name': '5 Minutes', 'yf_interval': '5m', 'max_days': 60},
    '15m': {'name': '15 Minutes', 'yf_interval': '15m', 'max_days': 60},
    '30m': {'name': '30 Minutes', 'yf_interval': '30m', 'max_days': 60},
    '1h': {'name': '1 Hour', 'yf_interval': '1h', 'max_days': 730},
    '4h': {'name': '4 Hours', 'yf_interval': '4h', 'max_days': 730},
    '1d': {'name': '1 Day', 'yf_interval': '1d', 'max_days': 3650},
    '1wk': {'name': '1 Week', 'yf_interval': '1wk', 'max_days': 3650},
}

# Default timeframes for user selection (most practical for forex)
DEFAULT_TIMEFRAMES = ['5m', '15m', '30m', '1h', '4h', '1d']

# ===== TRADING CONSTRAINTS =====

# Minimum position size (in base currency units)
MIN_POSITION_SIZE = 0.01  # Standard micro lot

# Maximum leverage by pair type
MAX_LEVERAGE = {
    'majors': 50,      # 50:1 for major pairs
    'crosses': 30,     # 30:1 for cross pairs
    'exotics': 10,     # 10:1 for exotic pairs (more risk)
}

# Margin requirements (as percentage)
MARGIN_REQUIREMENTS = {
    'majors': 0.02,    # 2% = 50:1 leverage
    'crosses': 0.033,  # 3.3% = 30:1 leverage
    'exotics': 0.10,   # 10% = 10:1 leverage
}

# ===== HELPER FUNCTIONS =====

def get_spread(pair: str, timeframe: str = '1h') -> float:
    """
    Get the realistic spread for a pair and timeframe.

    Parameters:
    -----------
    pair : str
        Forex pair (e.g., 'EURUSD')
    timeframe : str
        Timeframe (e.g., '5m', '1h', '1d')

    Returns:
    --------
    float
        Spread in decimal format

    Example:
    --------
    spread = get_spread('EURUSD', '5m')  # Returns ~0.00015 (1.5 pips)
    """
    pair = pair.upper().replace('/', '').replace('-', '')

    # Get base spread
    base_spread = PAIR_SPREADS.get(pair)
    if base_spread is None:
        # Default to 2 pips if pair not found
        print(f"⚠️  Warning: Unknown pair {pair}, using default spread of 2 pips")
        base_spread = 0.00020

    # Get timeframe multiplier
    multiplier = TIMEFRAME_SPREAD_MULTIPLIERS.get(timeframe, 1.0)

    # Calculate final spread
    final_spread = base_spread * multiplier

    return final_spread


def get_pair_type(pair: str) -> str:
    """
    Classify a forex pair as major, cross, or exotic.

    Parameters:
    -----------
    pair : str
        Forex pair (e.g., 'EURUSD')

    Returns:
    --------
    str
        'majors', 'crosses', or 'exotics'
    """
    pair = pair.upper().replace('/', '').replace('-', '')

    majors = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD']
    exotics = ['USDTRY', 'USDZAR', 'USDMXN', 'USDBRL']

    if pair in majors:
        return 'majors'
    elif pair in exotics:
        return 'exotics'
    else:
        return 'crosses'


def get_margin_requirement(pair: str) -> float:
    """
    Get the margin requirement for a pair.

    Parameters:
    -----------
    pair : str
        Forex pair (e.g., 'EURUSD')

    Returns:
    --------
    float
        Margin requirement (e.g., 0.02 = 2%)
    """
    pair_type = get_pair_type(pair)
    return MARGIN_REQUIREMENTS[pair_type]


def get_max_leverage(pair: str) -> int:
    """
    Get the maximum leverage for a pair.

    Parameters:
    -----------
    pair : str
        Forex pair (e.g., 'EURUSD')

    Returns:
    --------
    int
        Maximum leverage (e.g., 50 for 50:1)
    """
    pair_type = get_pair_type(pair)
    return MAX_LEVERAGE[pair_type]


def get_timeframe_info(timeframe: str) -> dict:
    """
    Get information about a timeframe.

    Parameters:
    -----------
    timeframe : str
        Timeframe code (e.g., '5m', '1h')

    Returns:
    --------
    dict
        Timeframe information with keys: name, yf_interval, max_days
    """
    return AVAILABLE_TIMEFRAMES.get(timeframe, {
        'name': timeframe,
        'yf_interval': timeframe,
        'max_days': 60
    })


def format_spread_pips(spread: float, pair: str) -> str:
    """
    Format spread in human-readable pips.

    Parameters:
    -----------
    spread : float
        Spread in decimal format
    pair : str
        Forex pair

    Returns:
    --------
    str
        Formatted spread (e.g., "1.5 pips")
    """
    pair = pair.upper()

    # JPY pairs have different pip calculation
    if 'JPY' in pair:
        pips = spread * 100  # 1 pip = 0.01 for JPY pairs
    else:
        pips = spread * 10000  # 1 pip = 0.0001 for other pairs

    return f"{pips:.1f} pips"


# ===== SPREAD SUMMARY =====

def print_spread_table():
    """Print a table of all spreads for different timeframes."""
    print("\n" + "="*80)
    print("  REALISTIC FOREX SPREADS")
    print("="*80)
    print(f"\n{'Pair':<10} {'1h Spread':<15} {'5m Spread':<15} {'1d Spread':<15} {'Type':<10}")
    print("-"*80)

    for pair in sorted(PAIR_SPREADS.keys()):
        spread_1h = format_spread_pips(get_spread(pair, '1h'), pair)
        spread_5m = format_spread_pips(get_spread(pair, '5m'), pair)
        spread_1d = format_spread_pips(get_spread(pair, '1d'), pair)
        pair_type = get_pair_type(pair)

        print(f"{pair:<10} {spread_1h:<15} {spread_5m:<15} {spread_1d:<15} {pair_type:<10}")

    print("="*80 + "\n")


if __name__ == '__main__':
    # Demo the configuration
    print_spread_table()

    print("\nExample spreads:")
    print(f"EURUSD 5m: {format_spread_pips(get_spread('EURUSD', '5m'), 'EURUSD')}")
    print(f"GBPJPY 15m: {format_spread_pips(get_spread('GBPJPY', '15m'), 'GBPJPY')}")
    print(f"USDTRY 1h: {format_spread_pips(get_spread('USDTRY', '1h'), 'USDTRY')}")
