"""
Forex Data Downloader

Downloads historical forex data from Yahoo Finance and caches it locally.
Automatically handles data caching to avoid unnecessary re-downloads.
"""

import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import os


# Forex pairs available for download
FOREX_PAIRS = {
    # Majors (most liquid)
    'EURUSD': 'EURUSD=X',
    'GBPUSD': 'GBPUSD=X',
    'USDJPY': 'USDJPY=X',
    'USDCHF': 'USDCHF=X',
    'AUDUSD': 'AUDUSD=X',
    'USDCAD': 'USDCAD=X',
    'NZDUSD': 'NZDUSD=X',

    # High volatility crosses
    'GBPJPY': 'GBPJPY=X',
    'EURJPY': 'EURJPY=X',
    'AUDJPY': 'AUDJPY=X',
    'NZDJPY': 'NZDJPY=X',
    'EURGBP': 'EURGBP=X',
    'EURAUD': 'EURAUD=X',

    # Exotics (extreme volatility)
    'USDTRY': 'USDTRY=X',
    'USDZAR': 'USDZAR=X',
    'USDMXN': 'USDMXN=X',
    'USDBRL': 'USDBRL=X',
}


class ForexDownloader:
    """
    Downloads and caches forex data from Yahoo Finance.

    Usage:
    ------
    downloader = ForexDownloader()

    # Download single pair
    data = downloader.download('EURUSD', start='2023-01-01', end='2024-01-01')

    # Download multiple pairs
    data_dict = downloader.download_multiple(['EURUSD', 'GBPUSD'])

    # Force re-download (ignore cache)
    data = downloader.download('EURUSD', force_download=True)
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize downloader.

        Parameters:
        -----------
        cache_dir : str, optional
            Directory to cache downloaded data. Defaults to data/csv/
        """
        if cache_dir is None:
            # Default to data/csv/ relative to project root
            project_root = Path(__file__).parent.parent
            cache_dir = project_root / 'data' / 'csv'

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def download(self,
                 pair: str,
                 start: Optional[str] = None,
                 end: Optional[str] = None,
                 interval: str = '1d',
                 force_download: bool = False) -> pd.DataFrame:
        """
        Download forex data for a single pair.

        Parameters:
        -----------
        pair : str
            Forex pair symbol (e.g., 'EURUSD', 'GBPUSD')
        start : str, optional
            Start date in YYYY-MM-DD format. Defaults to 2 years ago.
        end : str, optional
            End date in YYYY-MM-DD format. Defaults to today.
        interval : str, optional
            Data interval: '1d', '1h', '5m', etc. Default is '1d'.
        force_download : bool, optional
            If True, ignore cache and re-download. Default is False.

        Returns:
        --------
        pd.DataFrame
            OHLCV data with columns: Open, High, Low, Close, Volume
        """
        # Normalize pair name
        pair = pair.upper().replace('/', '').replace('-', '')

        # Get Yahoo Finance symbol
        if pair not in FOREX_PAIRS:
            raise ValueError(f"Unknown forex pair: {pair}. Available pairs: {list(FOREX_PAIRS.keys())}")

        yf_symbol = FOREX_PAIRS[pair]

        # Set default dates
        if end is None:
            end = datetime.now().strftime('%Y-%m-%d')
        if start is None:
            start = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')

        # Check cache
        cache_file = self._get_cache_filename(pair, start, end, interval)
        if not force_download and cache_file.exists():
            print(f"📂 Loading {pair} from cache...")
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)

        # Download from Yahoo Finance
        print(f"📥 Downloading {pair} data from {start} to {end}...")
        try:
            data = yf.download(
                yf_symbol,
                start=start,
                end=end,
                interval=interval,
                progress=False,
                auto_adjust=True  # Silence FutureWarning
            )

            if data.empty:
                raise ValueError(f"No data returned for {pair}")

            # Keep only OHLCV columns
            if isinstance(data.columns, pd.MultiIndex):
                # Handle multi-index columns (when downloading multiple symbols)
                data.columns = [col[0] for col in data.columns]

            data = data[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()

            # Save to cache
            data.to_csv(cache_file)
            print(f"✅ Downloaded {len(data)} bars of {pair} data")

            return data

        except Exception as e:
            print(f"❌ Error downloading {pair}: {e}")
            raise

    def download_multiple(self,
                          pairs: list[str],
                          start: Optional[str] = None,
                          end: Optional[str] = None,
                          interval: str = '1d',
                          force_download: bool = False) -> dict[str, pd.DataFrame]:
        """
        Download data for multiple forex pairs.

        Parameters:
        -----------
        pairs : list[str]
            List of forex pair symbols
        start : str, optional
            Start date in YYYY-MM-DD format
        end : str, optional
            End date in YYYY-MM-DD format
        interval : str, optional
            Data interval
        force_download : bool, optional
            If True, ignore cache and re-download

        Returns:
        --------
        dict[str, pd.DataFrame]
            Dictionary mapping pair names to dataframes
        """
        results = {}
        for pair in pairs:
            try:
                results[pair] = self.download(pair, start, end, interval, force_download)
            except Exception as e:
                print(f"⚠️  Skipping {pair}: {e}")
                continue

        return results

    def get_available_pairs(self) -> list[str]:
        """Get list of available forex pairs."""
        return list(FOREX_PAIRS.keys())

    def clear_cache(self, pair: Optional[str] = None):
        """
        Clear cached data.

        Parameters:
        -----------
        pair : str, optional
            If specified, only clear cache for this pair.
            Otherwise, clear all cached data.
        """
        if pair:
            pattern = f"{pair.upper()}_*.csv"
            files = list(self.cache_dir.glob(pattern))
        else:
            files = list(self.cache_dir.glob("*.csv"))

        for file in files:
            file.unlink()
            print(f"🗑️  Deleted {file.name}")

        print(f"✅ Cleared {len(files)} cached file(s)")

    def _get_cache_filename(self, pair: str, start: str, end: str, interval: str) -> Path:
        """Generate cache filename based on download parameters."""
        # Normalize dates to remove hyphens
        start_str = start.replace('-', '')
        end_str = end.replace('-', '')
        filename = f"{pair}_{start_str}_{end_str}_{interval}.csv"
        return self.cache_dir / filename


# ===== CONVENIENCE FUNCTIONS =====

def download_forex_data(pair: str,
                        start: Optional[str] = None,
                        end: Optional[str] = None,
                        force_download: bool = False) -> pd.DataFrame:
    """
    Convenience function to download forex data.

    Example:
    --------
    from data.downloader import download_forex_data
    data = download_forex_data('EURUSD', start='2023-01-01')
    """
    downloader = ForexDownloader()
    return downloader.download(pair, start, end, force_download=force_download)


def list_available_pairs() -> list[str]:
    """List all available forex pairs."""
    return list(FOREX_PAIRS.keys())


# ===== CLI INTERFACE =====

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Download forex data')
    parser.add_argument('pairs', nargs='+', help='Forex pairs to download (e.g., EURUSD GBPUSD)')
    parser.add_argument('--start', type=str, help='Start date (YYYY-MM-DD)', default=None)
    parser.add_argument('--end', type=str, help='End date (YYYY-MM-DD)', default=None)
    parser.add_argument('--force', action='store_true', help='Force re-download (ignore cache)')
    parser.add_argument('--list', action='store_true', help='List available pairs')
    parser.add_argument('--clear-cache', action='store_true', help='Clear all cached data')

    args = parser.parse_args()

    downloader = ForexDownloader()

    if args.list:
        print("Available forex pairs:")
        for pair in downloader.get_available_pairs():
            print(f"  - {pair}")
        exit(0)

    if args.clear_cache:
        downloader.clear_cache()
        exit(0)

    # Download requested pairs
    for pair in args.pairs:
        try:
            data = downloader.download(
                pair,
                start=args.start,
                end=args.end,
                force_download=args.force
            )
            print(f"✅ {pair}: {len(data)} bars downloaded")
        except Exception as e:
            print(f"❌ {pair}: {e}")