"""TradingView data collection module using tradingview_ta."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from tradingview_ta import TA_Handler, Interval

from src.config import SCREENER_MAP

logger = logging.getLogger(__name__)

INTERVAL_MAP = {
    "1m": Interval.INTERVAL_1_MINUTE,
    "5m": Interval.INTERVAL_5_MINUTES,
    "15m": Interval.INTERVAL_15_MINUTES,
    "1h": Interval.INTERVAL_1_HOUR,
    "4h": Interval.INTERVAL_4_HOURS,
    "1d": Interval.INTERVAL_1_DAY,
    "1W": Interval.INTERVAL_1_WEEK,
    "1M": Interval.INTERVAL_1_MONTH,
}

# Fallback screener values to try if the primary one fails
SCREENER_FALLBACKS = {
    "cfd": ["america"],
    "america": ["cfd"],
    "korea": [],
    "forex": [],
    "crypto": [],
}


@dataclass
class MarketData:
    """Container for market data from TradingView."""

    symbol: str
    exchange: str
    name: str
    close: float
    open_price: float
    high: float
    low: float
    volume: float
    change: float
    change_pct: float
    indicators: dict
    oscillators: dict
    moving_averages: dict
    summary: dict


def _parse_exchange_symbol(tv_symbol: str) -> tuple[str, str]:
    """Parse 'EXCHANGE:SYMBOL' format into (exchange, symbol)."""
    if ":" in tv_symbol:
        exchange, symbol = tv_symbol.split(":", 1)
        return exchange, symbol
    return "", tv_symbol


def _get_screener(exchange: str) -> str:
    """Get the screener name for a given exchange."""
    return SCREENER_MAP.get(exchange, "america")


def _safe_get(indicators: dict, key: str, default=0):
    """Safely get a value from indicators, returning default if None."""
    val = indicators.get(key)
    return val if val is not None else default


def _try_fetch(symbol: str, screener: str, exchange: str, tv_interval):
    """Attempt to fetch analysis with given screener, return Analysis or None."""
    try:
        handler = TA_Handler(
            symbol=symbol,
            screener=screener,
            exchange=exchange,
            interval=tv_interval,
        )
        return handler.get_analysis()
    except Exception as e:
        logger.debug("Screener '%s' failed for %s:%s - %s", screener, exchange, symbol, e)
        return None


def fetch_analysis(
    tv_symbol: str,
    interval: str = "1d",
    display_name: str = "",
) -> MarketData | None:
    """Fetch technical analysis data from TradingView.

    Args:
        tv_symbol: TradingView symbol in 'EXCHANGE:SYMBOL' format.
        interval: Time interval string (e.g. '1d', '1h').
        display_name: Human-readable name for the asset.

    Returns:
        MarketData instance or None if the fetch fails.
    """
    exchange, symbol = _parse_exchange_symbol(tv_symbol)
    primary_screener = _get_screener(exchange)
    tv_interval = INTERVAL_MAP.get(interval, Interval.INTERVAL_1_DAY)

    # Try primary screener first, then fallbacks
    screeners_to_try = [primary_screener] + SCREENER_FALLBACKS.get(primary_screener, [])
    analysis = None

    for screener in screeners_to_try:
        analysis = _try_fetch(symbol, screener, exchange, tv_interval)
        if analysis is not None:
            break

    if analysis is None:
        logger.warning("All screeners failed for %s", tv_symbol)
        return None

    try:
        indicators = analysis.indicators or {}
        close = _safe_get(indicators, "close", 0)
        open_price = _safe_get(indicators, "open", 0)
        high = _safe_get(indicators, "high", 0)
        low = _safe_get(indicators, "low", 0)
        volume = _safe_get(indicators, "volume", 0)
        change = _safe_get(indicators, "change", 0)
        change_pct = (change / open_price * 100) if open_price else 0

        summary = analysis.summary or {"RECOMMENDATION": "NEUTRAL", "BUY": 0, "SELL": 0, "NEUTRAL": 0}
        oscillators = analysis.oscillators or {"RECOMMENDATION": "NEUTRAL", "COMPUTE": {"BUY": 0, "SELL": 0, "NEUTRAL": 0}}
        moving_averages = analysis.moving_averages or {"RECOMMENDATION": "NEUTRAL", "COMPUTE": {"BUY": 0, "SELL": 0, "NEUTRAL": 0}}

        return MarketData(
            symbol=symbol,
            exchange=exchange,
            name=display_name or symbol,
            close=close,
            open_price=open_price,
            high=high,
            low=low,
            volume=volume,
            change=change,
            change_pct=change_pct,
            indicators=indicators,
            oscillators=oscillators,
            moving_averages=moving_averages,
            summary=summary,
        )
    except Exception:
        logger.exception("Error processing data for %s", tv_symbol)
        return None


def fetch_multiple(
    symbols: dict[str, tuple[str, str]],
    interval: str = "1d",
) -> dict[str, MarketData]:
    """Fetch analysis for multiple symbols.

    Args:
        symbols: Mapping of key -> (tv_symbol, display_name).
        interval: Time interval.

    Returns:
        Dict of key -> MarketData for successful fetches.
    """
    results: dict[str, MarketData] = {}
    for key, (tv_symbol, display_name) in symbols.items():
        data = fetch_analysis(tv_symbol, interval, display_name)
        if data is not None:
            results[key] = data
        # Small delay to avoid rate-limiting
        time.sleep(0.2)
    return results
