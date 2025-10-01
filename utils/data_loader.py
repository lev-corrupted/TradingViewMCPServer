"""
Data Loader Utility

Provides unified interface for loading forex data from various sources:
- Local CSV files
- Cached data
- Fresh downloads from Yahoo Finance
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from data.downloader import ForexDownloader, FOREX_PAIRS


class DataLoader:
    """
    Unified data loading interface for backtesting.

    Automatically handles:
    - Loading from cache if available
    - Downloading if not cached
    - CSV file loading
    - Data validation

    Usage:
    ------
    loader = DataLoader()

    # Load data (auto-downloads if needed)
    data = loader.load('EURUSD', start='2023-01-01', end='2024-01-01')

    # Load from specific CSV file
    data = loader.load_csv('path/to/data.csv')

    # Load multiple pairs
    data_dict = loader.load_multiple(['EURUSD', 'GBPUSD'])
    """

    def __init__(self):
        """Initialize data loader with downloader."""
        self.downloader = ForexDownloader()

    def load(self,
             pair: str,
             start: Optional[str] = None,
             end: Optional[str] = None,
             interval: str = '1d',
             source: str = 'auto') -> pd.DataFrame:
        """
        Load forex data from the best available source.

        Parameters:
        -----------
        pair : str
            Forex pair symbol (e.g., 'EURUSD', 'GBPUSD')
        start : str, optional
            Start date in YYYY-MM-DD format
        end : str, optional
            End date in YYYY-MM-DD format
        interval : str, optional
            Data interval: '1d', '1h', etc.
        source : str, optional
            Data source: 'auto' (default), 'cache', 'download', 'csv'

        Returns:
        --------
        pd.DataFrame
            OHLCV data
        """
        if source == 'download':
            # Force fresh download
            return self.downloader.download(pair, start, end, interval, force_download=True)

        elif source == 'cache':
            # Only load from cache, fail if not available
            data = self.downloader.download(pair, start, end, interval, force_download=False)
            return data

        else:  # auto
            # Try cache first, download if needed
            return self.downloader.download(pair, start, end, interval, force_download=False)

    def load_csv(self,
                 filepath: str,
                 date_column: Optional[str] = None) -> pd.DataFrame:
        """
        Load data from a CSV file.

        Parameters:
        -----------
        filepath : str
            Path to CSV file
        date_column : str, optional
            Name of date column. If None, uses index.

        Returns:
        --------
        pd.DataFrame
            OHLCV data
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        # Load CSV
        if date_column:
            data = pd.read_csv(filepath, parse_dates=[date_column])
            data = data.set_index(date_column)
        else:
            data = pd.read_csv(filepath, index_col=0, parse_dates=True)

        # Validate data
        data = self._validate_data(data)

        return data

    def load_multiple(self,
                      pairs: list[str],
                      start: Optional[str] = None,
                      end: Optional[str] = None,
                      interval: str = '1d') -> dict[str, pd.DataFrame]:
        """
        Load data for multiple forex pairs.

        Parameters:
        -----------
        pairs : list[str]
            List of forex pair symbols
        start : str, optional
            Start date
        end : str, optional
            End date
        interval : str, optional
            Data interval

        Returns:
        --------
        dict[str, pd.DataFrame]
            Dictionary mapping pair names to dataframes
        """
        return self.downloader.download_multiple(pairs, start, end, interval)

    def get_available_pairs(self) -> list[str]:
        """Get list of available forex pairs."""
        return self.downloader.get_available_pairs()

    def _validate_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and clean OHLCV data.

        Checks:
        - Has required columns (Open, High, Low, Close)
        - Index is datetime
        - No NaN values in critical columns
        - Proper OHLC relationships (High >= Open, Close >= Low, etc.)
        """
        # Check required columns
        required_cols = ['Open', 'High', 'Low', 'Close']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Ensure datetime index
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data index must be DatetimeIndex")

        # Drop rows with NaN in critical columns
        data = data.dropna(subset=required_cols)

        # Add Volume column if missing
        if 'Volume' not in data.columns:
            data['Volume'] = 0

        # Sort by date
        data = data.sort_index()

        # Basic OHLC validation
        invalid_rows = (
            (data['High'] < data['Low']) |
            (data['High'] < data['Open']) |
            (data['High'] < data['Close']) |
            (data['Low'] > data['Open']) |
            (data['Low'] > data['Close'])
        )

        if invalid_rows.any():
            n_invalid = invalid_rows.sum()
            print(f"⚠️  Warning: Found {n_invalid} rows with invalid OHLC relationships. Removing...")
            data = data[~invalid_rows]

        return data


# ===== CONVENIENCE FUNCTIONS =====

def load_forex_data(pair: str,
                    start: Optional[str] = None,
                    end: Optional[str] = None) -> pd.DataFrame:
    """
    Quick function to load forex data.

    Example:
    --------
    from utils.data_loader import load_forex_data
    data = load_forex_data('EURUSD', start='2023-01-01')
    """
    loader = DataLoader()
    return loader.load(pair, start, end)


def load_multiple_pairs(pairs: list[str],
                        start: Optional[str] = None,
                        end: Optional[str] = None) -> dict[str, pd.DataFrame]:
    """
    Quick function to load multiple forex pairs.

    Example:
    --------
    from utils.data_loader import load_multiple_pairs
    data = load_multiple_pairs(['EURUSD', 'GBPUSD'], start='2023-01-01')
    """
    loader = DataLoader()
    return loader.load_multiple(pairs, start, end)