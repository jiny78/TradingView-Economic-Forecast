"""TradingView data collection module using tradingview_ta."""

from __future__ import annotations

import logging
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
    screener = _get_screener(exchange)
    tv_interval = INTERVAL_MAP.get(interval, Interval.INTERVAL_1_DAY)

    try:
        handler = TA_Handler(
            symbol=symbol,
            screener=screener,
            exchange=exchange,
            interval=tv_interval,
        )
        analysis = handler.get_analysis()
    except Exception:
        logger.exception("Failed to fetch data for %s", tv_symbol)
        return None

    indicators = analysis.indicators
    close = indicators.get("close", 0)
    open_price = indicators.get("open", 0)
    high = indicators.get("high", 0)
    low = indicators.get("low", 0)
    volume = indicators.get("volume", 0)
    change = indicators.get("change", 0)
    change_pct = (change / open_price * 100) if open_price else 0

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
        oscillators=analysis.oscillators,
        moving_averages=analysis.moving_averages,
        summary=analysis.summary,
    )


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
    return results
