"""
Portfolio analytics: per-holding and portfolio-level metrics,
including a simple volatility (risk) measure from historical prices.
"""

import statistics
from datetime import datetime

import db


def analyze_holding(holding: dict) -> dict:
    symbol = holding["symbol"]
    history = db.get_price_history(symbol)
    if not history:
        raise ValueError(f"No price history for {symbol}. Run price update first.")

    current_price = history[-1][1]
    quantity = holding["quantity"]
    buy_price = holding["buy_price"]

    invested = round(quantity * buy_price, 2)
    current_value = round(quantity * current_price, 2)
    gain_loss = round(current_value - invested, 2)
    gain_loss_pct = round((gain_loss / invested) * 100, 2) if invested else 0.0

    closes = [p for _, p in history]
    daily_returns = [(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, len(closes)) if closes[i - 1]]
    volatility_pct = round(statistics.pstdev(daily_returns) * 100, 2) if len(daily_returns) > 1 else 0.0

    holding_days = (datetime.now() - datetime.strptime(holding["buy_date"], "%Y-%m-%d")).days

    return {
        "symbol": symbol,
        "company_name": holding["company_name"],
        "sector": holding["sector"],
        "quantity": quantity,
        "buy_price": buy_price,
        "current_price": current_price,
        "invested": invested,
        "current_value": current_value,
        "gain_loss": gain_loss,
        "gain_loss_pct": gain_loss_pct,
        "daily_volatility_pct": volatility_pct,
        "holding_days": holding_days,
    }


def analyze_portfolio(holdings: list) -> dict:
    rows = [analyze_holding(h) for h in holdings]

    total_invested = round(sum(r["invested"] for r in rows), 2)
    total_current_value = round(sum(r["current_value"] for r in rows), 2)
    total_gain_loss = round(total_current_value - total_invested, 2)
    total_return_pct = round((total_gain_loss / total_invested) * 100, 2) if total_invested else 0.0

    for r in rows:
        r["weight_pct"] = round((r["current_value"] / total_current_value) * 100, 2) if total_current_value else 0.0

    sector_allocation = {}
    for r in rows:
        sector_allocation.setdefault(r["sector"], 0.0)
        sector_allocation[r["sector"]] += r["current_value"]
    sector_allocation = {k: round(v, 2) for k, v in sector_allocation.items()}

    best = max(rows, key=lambda r: r["gain_loss_pct"]) if rows else None
    worst = min(rows, key=lambda r: r["gain_loss_pct"]) if rows else None

    return {
        "holdings": rows,
        "total_invested": total_invested,
        "total_current_value": total_current_value,
        "total_gain_loss": total_gain_loss,
        "total_return_pct": total_return_pct,
        "sector_allocation": sector_allocation,
        "best_performer": best,
        "worst_performer": worst,
    }