"""
Stock Market Portfolio Analyzer
--------------------------------
Tracks a stock portfolio in SQLite, fetches price history (live via
yfinance, or simulated offline), computes performance/risk metrics,
and generates a formatted Excel report.

Usage:
    python main.py            # seeds a sample portfolio (first run), analyzes, reports
    python main.py --refresh  # re-fetch prices even if already cached
"""

import sys
import argparse

import db
import price_fetcher
import analyzer
import report_generator

SAMPLE_PORTFOLIO = [
    ("RELIANCE", "Reliance Industries", "Energy", 10, 2450.0, "2025-08-15"),
    ("TCS", "Tata Consultancy Services", "IT", 5, 3600.0, "2025-09-01"),
    ("INFY", "Infosys", "IT", 15, 1450.0, "2025-07-20"),
    ("HDFCBANK", "HDFC Bank", "Banking", 12, 1550.0, "2025-10-05"),
    ("ICICIBANK", "ICICI Bank", "Banking", 20, 1100.0, "2025-06-10"),
    ("ITC", "ITC Limited", "FMCG", 30, 430.0, "2025-11-01"),
    ("TATAMOTORS", "Tata Motors", "Automobile", 25, 850.0, "2025-05-15"),
]


def seed_sample_portfolio():
    for symbol, name, sector, qty, price, date in SAMPLE_PORTFOLIO:
        db.add_holding(symbol, name, sector, qty, price, date)
    print(f"Seeded {len(SAMPLE_PORTFOLIO)} sample holdings.")


def update_prices(holdings, force_refresh=False):
    for h in holdings:
        symbol = h["symbol"]
        if not force_refresh and db.get_latest_price(symbol):
            continue
        history, source = price_fetcher.get_price_history(symbol)
        db.save_price_history(symbol, history)
        print(f"  {symbol}: {len(history)} price points loaded ({source})")


def print_console_summary(result):
    print("\n" + "=" * 55)
    print("PORTFOLIO SUMMARY")
    print("=" * 55)
    print(f"Total Invested   : Rs. {result['total_invested']:,.2f}")
    print(f"Current Value    : Rs. {result['total_current_value']:,.2f}")
    print(f"Gain/Loss        : Rs. {result['total_gain_loss']:,.2f} ({result['total_return_pct']}%)")
    print(f"Best Performer   : {result['best_performer']['symbol']} ({result['best_performer']['gain_loss_pct']}%)")
    print(f"Worst Performer  : {result['worst_performer']['symbol']} ({result['worst_performer']['gain_loss_pct']}%)")
    print("=" * 55)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Re-fetch prices even if cached")
    parser.add_argument("--output", default=None, help="Output Excel file path")
    args = parser.parse_args()

    db.init_db()
    holdings = db.get_holdings()
    if not holdings:
        seed_sample_portfolio()
        holdings = db.get_holdings()

    print("Fetching price data...")
    update_prices(holdings, force_refresh=args.refresh)

    result = analyzer.analyze_portfolio(holdings)
    print_console_summary(result)

    output_path = report_generator.generate_report(result, args.output)
    print(f"\nExcel report generated: {output_path}")


if __name__ == "__main__":
    main()