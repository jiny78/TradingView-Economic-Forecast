"""Flask web dashboard with TradingView widgets and forecast display."""

from __future__ import annotations

import logging

from flask import Flask, render_template, jsonify, request

from src.config import SYMBOLS, INTERVALS, DEFAULT_INTERVAL
from src.data.collector import fetch_analysis, fetch_multiple
from src.analysis.technical import analyze, analyze_multiple
from src.forecast.predictor import predict, predict_multiple

logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)


@app.route("/")
def index():
    """Main dashboard page."""
    return render_template("index.html", symbols=SYMBOLS, intervals=INTERVALS)


@app.route("/api/analyze", methods=["GET"])
def api_analyze():
    """Analyze a single symbol."""
    tv_symbol = request.args.get("symbol", "SP:SPX")
    interval = request.args.get("interval", DEFAULT_INTERVAL)
    name = request.args.get("name", "")

    data = fetch_analysis(tv_symbol, interval, name)
    if data is None:
        return jsonify({"error": f"Failed to fetch data for {tv_symbol}"}), 400

    analysis = analyze(data)
    forecast = predict(data)

    return jsonify({
        "analysis": {
            "symbol": analysis.symbol,
            "name": analysis.name,
            "price": analysis.price,
            "change_pct": round(analysis.change_pct, 2),
            "summary": analysis.summary_recommendation,
            "summary_kr": analysis.summary_kr,
            "summary_score": analysis.summary_score,
            "oscillator": analysis.oscillator_recommendation,
            "oscillator_kr": analysis.oscillator_kr,
            "oscillator_counts": {
                "buy": analysis.oscillator_buy,
                "sell": analysis.oscillator_sell,
                "neutral": analysis.oscillator_neutral,
            },
            "ma": analysis.ma_recommendation,
            "ma_kr": analysis.ma_kr,
            "ma_counts": {
                "buy": analysis.ma_buy,
                "sell": analysis.ma_sell,
                "neutral": analysis.ma_neutral,
            },
            "trend": analysis.trend,
            "key_levels": analysis.key_levels,
        },
        "forecast": {
            "symbol": forecast.symbol,
            "name": forecast.name,
            "current_price": forecast.current_price,
            "direction": forecast.direction,
            "direction_kr": forecast.direction_kr,
            "direction_emoji": forecast.direction_emoji,
            "confidence": forecast.confidence,
            "signal_strength": forecast.signal_strength,
            "factors": forecast.factors,
        },
    })


@app.route("/api/overview", methods=["GET"])
def api_overview():
    """Get overview for all configured symbols."""
    interval = request.args.get("interval", DEFAULT_INTERVAL)
    category = request.args.get("category", "all")

    if category == "all":
        all_symbols = {}
        for cat_symbols in SYMBOLS.values():
            all_symbols.update(cat_symbols)
    else:
        all_symbols = SYMBOLS.get(category, {})

    market_data = fetch_multiple(all_symbols, interval)
    analyses = analyze_multiple(market_data)
    forecasts = predict_multiple(market_data)

    results = []
    for key in analyses:
        a = analyses[key]
        f = forecasts[key]
        results.append({
            "key": key,
            "symbol": a.symbol,
            "name": a.name,
            "price": a.price,
            "change_pct": round(a.change_pct, 2),
            "summary": a.summary_recommendation,
            "summary_kr": a.summary_kr,
            "trend": a.trend,
            "direction": f.direction,
            "direction_kr": f.direction_kr,
            "direction_emoji": f.direction_emoji,
            "confidence": f.confidence,
            "signal_strength": f.signal_strength,
        })

    return jsonify({"results": results, "count": len(results)})


def create_app() -> Flask:
    """Application factory."""
    logging.basicConfig(level=logging.INFO)
    return app
