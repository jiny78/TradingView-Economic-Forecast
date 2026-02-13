#!/usr/bin/env python3
"""TradingView Economic Forecast - Main entry point.

Usage:
    python main.py              # Start web dashboard
    python main.py --cli        # Run CLI analysis
    python main.py --cli -s SPX # Analyze specific symbol
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

from src.config import SYMBOLS, DEFAULT_INTERVAL, FLASK_HOST, FLASK_PORT, FLASK_DEBUG


def run_cli(symbol_key: str | None, category: str, interval: str) -> None:
    """Run analysis in CLI mode and print results."""
    from src.data.collector import fetch_analysis, fetch_multiple
    from src.analysis.technical import analyze, analyze_multiple
    from src.forecast.predictor import predict, predict_multiple

    if symbol_key:
        # Find symbol in config
        tv_symbol = None
        display_name = ""
        for cat_symbols in SYMBOLS.values():
            if symbol_key.upper() in cat_symbols:
                tv_symbol, display_name = cat_symbols[symbol_key.upper()]
                break

        if tv_symbol is None:
            print(f"Error: Unknown symbol '{symbol_key}'")
            print(f"Available symbols: {', '.join(k for cs in SYMBOLS.values() for k in cs)}")
            sys.exit(1)

        print(f"\n  Analyzing {display_name} ({symbol_key.upper()})...")
        data = fetch_analysis(tv_symbol, interval, display_name)
        if data is None:
            print("  Failed to fetch data.")
            sys.exit(1)

        a = analyze(data)
        f = predict(data)

        print(f"\n{'=' * 60}")
        print(f"  {a.name} ({a.symbol})")
        print(f"{'=' * 60}")
        print(f"  Price:      {a.price:,.2f}")
        print(f"  Change:     {a.change_pct:+.2f}%")
        print(f"  Trend:      {a.trend}")
        print(f"{'─' * 60}")
        print(f"  Technical Analysis")
        print(f"    Summary:      {a.summary_kr} ({a.summary_recommendation})")
        print(f"    Oscillators:  {a.oscillator_kr} (Buy:{a.oscillator_buy} Neutral:{a.oscillator_neutral} Sell:{a.oscillator_sell})")
        print(f"    Moving Avg:   {a.ma_kr} (Buy:{a.ma_buy} Neutral:{a.ma_neutral} Sell:{a.ma_sell})")
        print(f"{'─' * 60}")
        print(f"  Forecast")
        print(f"    Direction:    {f.direction_emoji} {f.direction_kr} ({f.direction})")
        print(f"    Confidence:   {f.confidence * 100:.1f}%")
        print(f"    Signal:       {f.signal_strength}")
        print(f"{'─' * 60}")
        print(f"  Key Factors:")
        for key, val in f.factors.items():
            print(f"    {key:15s} {val}")
        if a.key_levels:
            print(f"{'─' * 60}")
            print(f"  Key Levels:")
            for key, val in a.key_levels.items():
                print(f"    {key:10s} {val:,.4f}")
        print(f"{'=' * 60}\n")
    else:
        # Analyze category or all
        if category == "all":
            all_symbols = {}
            for cat_symbols in SYMBOLS.values():
                all_symbols.update(cat_symbols)
        else:
            all_symbols = SYMBOLS.get(category, {})

        if not all_symbols:
            print(f"Error: Unknown category '{category}'")
            print(f"Available: all, {', '.join(SYMBOLS.keys())}")
            sys.exit(1)

        print(f"\n  Fetching data for {len(all_symbols)} symbols...")
        market_data = fetch_multiple(all_symbols, interval)
        analyses = analyze_multiple(market_data)
        forecasts = predict_multiple(market_data)

        print(f"\n{'=' * 90}")
        print(f"  {'Symbol':<10} {'Name':<20} {'Price':>12} {'Change':>8} {'Analysis':<12} {'Forecast':<10} {'Conf':>6}")
        print(f"{'─' * 90}")
        for key in analyses:
            a = analyses[key]
            f = forecasts[key]
            change_str = f"{a.change_pct:+.2f}%"
            conf_str = f"{f.confidence * 100:.0f}%"
            print(f"  {a.symbol:<10} {a.name:<20} {a.price:>12,.2f} {change_str:>8} {a.summary_kr:<12} {f.direction_emoji} {f.direction_kr:<8} {conf_str:>6}")
        print(f"{'=' * 90}")
        print(f"  Total: {len(analyses)} symbols analyzed\n")


def run_web() -> None:
    """Start the Flask web dashboard."""
    from src.web.app import create_app

    app = create_app()
    print(f"\n  TradingView Economic Forecast Dashboard")
    print(f"  Starting server at http://{FLASK_HOST}:{FLASK_PORT}")
    print(f"  Press Ctrl+C to stop\n")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TradingView Economic Forecast Program"
    )
    parser.add_argument(
        "--cli", action="store_true", help="Run in CLI mode (default: web dashboard)"
    )
    parser.add_argument(
        "-s", "--symbol", type=str, default=None, help="Symbol to analyze (e.g., SPX, BTCUSD)"
    )
    parser.add_argument(
        "-c", "--category", type=str, default="all",
        help="Category: all, indices, forex, crypto, commodities"
    )
    parser.add_argument(
        "-i", "--interval", type=str, default=DEFAULT_INTERVAL,
        help="Interval: 1m, 5m, 15m, 1h, 4h, 1d, 1W, 1M"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results as JSON (CLI mode only)"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if args.cli:
        run_cli(args.symbol, args.category, args.interval)
    else:
        run_web()


if __name__ == "__main__":
    main()
