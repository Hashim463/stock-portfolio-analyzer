"""
Price data provider.

Tries to fetch real historical prices via yfinance (Yahoo Finance).
If there's no internet access (or the ticker fails), falls back to a
seeded random-walk simulator so the rest of the pipeline is always
demoable offline.
"""

import random
from datetime import datetime, timedelta

SEED_PRICES = {
    "RELIANCE": 2950.0,
    "TCS": 3850.0,
    "INFY": 1620.0,
    "HDFCBANK": 1680.0,
    "ICICIBANK": 1210.0,
    "ITC": 465.0,
    "SBIN": 830.0,
    "WIPRO": 545.0,
    "TATAMOTORS": 980.0,
    "MARUTI": 12500.0,
}


def fetch_live_history(symbol: str, period_days: int = 365):
    """Try real Yahoo Finance data (symbol.NS for NSE). Returns None on failure."""
    try:
        import yfinance as yf
        ticker = yf.Ticker(f"{symbol}.NS")
        hist = ticker.history(period=f"{period_days}d")
        if hist.empty:
            return None
        return [(idx.strftime("%Y-%m-%d"), round(float(row["Close"]), 2)) for idx, row in hist.iterrows()]
    except Exception:
        return None


def generate_mock_history(symbol: str, period_days: int = 365, seed: int = None):
    """Random-walk price simulator, seeded per symbol so results are repeatable."""
    rng = random.Random(seed if seed is not None else hash(symbol) % (2**32))
    base_price = SEED_PRICES.get(symbol, rng.uniform(200, 3000))

    prices = []
    price = base_price * rng.uniform(0.85, 0.95)
    start_date = datetime.now() - timedelta(days=period_days)

    for i in range(period_days):
        date = start_date + timedelta(days=i)
        if date.weekday() >= 5:
            continue
        drift = rng.uniform(-0.02, 0.022)
        price = max(price * (1 + drift), 1)
        prices.append((date.strftime("%Y-%m-%d"), round(price, 2)))

    if prices:
        prices[-1] = (prices[-1][0], round(base_price, 2))
    return prices


def get_price_history(symbol: str, period_days: int = 365, use_live: bool = True):
    if use_live:
        live = fetch_live_history(symbol, period_days)
        if live:
            return live, "live"
    return generate_mock_history(symbol, period_days), "simulated"