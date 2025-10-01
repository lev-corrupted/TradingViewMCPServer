#!/usr/bin/env python3
"""
Download data from TradingView to compare with yfinance data
This helps validate your backtesting system against TradingView's data
"""

import requests
import pandas as pd
import json
from datetime import datetime
import yfinance as yf

def get_tradingview_data(symbol, timeframe='1D', exchange='FX_IDC'):
    """
    Fetch data from TradingView Scanner API

    Timeframes: 1m, 5m, 15m, 1h, 4h, 1D, 1W, 1M
    Exchanges: FX_IDC (forex), BINANCE (crypto), NASDAQ, NYSE
    """

    url = "https://scanner.tradingview.com/forex/scan"

    payload = {
        "symbols": {
            "tickers": [f"{exchange}:{symbol}"],
        },
        "columns": [
            "name", "close", "volume", "change",
            "Recommend.All", "RSI", "MACD.macd", "MACD.signal",
            "BB.upper", "BB.lower", "EMA10", "SMA10", "EMA20", "SMA20"
        ]
    }

    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if 'data' in data and len(data['data']) > 0:
            return data['data'][0]
        else:
            return None
    except Exception as e:
        print(f"Error fetching TradingView data: {e}")
        return None

def compare_data_sources(symbol="EURUSD"):
    """Compare TradingView data vs yfinance data"""

    print("="*70)
    print(f"DATA COMPARISON: TradingView vs yfinance - {symbol}")
    print("="*70)

    # Get TradingView data
    print("\n📊 Fetching TradingView data...")
    tv_data = get_tradingview_data(symbol)

    if tv_data:
        print(f"✅ TradingView Current Price: ${tv_data['d'][1]:.5f}")
        print(f"   RSI: {tv_data['d'][5]:.2f}")
        print(f"   Recommendation: {tv_data['d'][4]}")

    # Get yfinance data
    print("\n📈 Fetching yfinance data...")
    yf_data = yf.download(f"{symbol}=X", period="5d", progress=False)

    # Fix MultiIndex columns if present
    if isinstance(yf_data.columns, pd.MultiIndex):
        yf_data.columns = yf_data.columns.droplevel(1)

    if len(yf_data) > 0:
        latest = yf_data.iloc[-1]
        close_price = float(latest['Close'])
        volume = float(latest['Volume'])
        print(f"✅ yfinance Latest Close: ${close_price:.5f}")
        print(f"   Volume: {volume:.0f}")
        print(f"   Date: {yf_data.index[-1].strftime('%Y-%m-%d')}")

    # Compare
    if tv_data and len(yf_data) > 0:
        tv_price = tv_data['d'][1]
        yf_price = float(latest['Close'])
        difference = abs(tv_price - yf_price)
        percent_diff = (difference / tv_price) * 100

        print("\n" + "="*70)
        print("COMPARISON RESULTS")
        print("="*70)
        print(f"Price Difference: ${difference:.5f} ({percent_diff:.3f}%)")

        if percent_diff < 0.1:
            print("✅ Data sources match closely! Your backtesting should be accurate.")
        else:
            print("⚠️  Significant difference detected. Check data sources.")

if __name__ == "__main__":
    # Test major forex pairs
    pairs = ["EURUSD", "GBPUSD", "USDJPY"]

    for pair in pairs:
        compare_data_sources(pair)
        print("\n")
