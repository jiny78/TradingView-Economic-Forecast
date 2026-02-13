"""Technical analysis module – interprets TradingView oscillators,
moving averages, and summary recommendations."""

from __future__ import annotations

from dataclasses import dataclass
from src.data.collector import MarketData


# Recommendation labels in order of bearish -> bullish
RECOMMENDATION_ORDER = [
    "STRONG_SELL",
    "SELL",
    "NEUTRAL",
    "BUY",
    "STRONG_BUY",
]

RECOMMENDATION_KR = {
    "STRONG_SELL": "강력 매도",
    "SELL": "매도",
    "NEUTRAL": "중립",
    "BUY": "매수",
    "STRONG_BUY": "강력 매수",
}

SIGNAL_SCORE = {
    "STRONG_SELL": -2,
    "SELL": -1,
    "NEUTRAL": 0,
    "BUY": 1,
    "STRONG_BUY": 2,
}


@dataclass
class AnalysisResult:
    """Aggregated technical analysis result."""

    symbol: str
    name: str
    price: float
    change_pct: float
    summary_recommendation: str
    summary_score: int
    oscillator_recommendation: str
    oscillator_buy: int
    oscillator_sell: int
    oscillator_neutral: int
    ma_recommendation: str
    ma_buy: int
    ma_sell: int
    ma_neutral: int
    key_levels: dict
    trend: str

    @property
    def summary_kr(self) -> str:
        return RECOMMENDATION_KR.get(self.summary_recommendation, self.summary_recommendation)

    @property
    def oscillator_kr(self) -> str:
        return RECOMMENDATION_KR.get(self.oscillator_recommendation, self.oscillator_recommendation)

    @property
    def ma_kr(self) -> str:
        return RECOMMENDATION_KR.get(self.ma_recommendation, self.ma_recommendation)


def _detect_trend(data: MarketData) -> str:
    """Detect basic trend from moving average positions."""
    indicators = data.indicators
    ema20 = indicators.get("EMA20")
    ema50 = indicators.get("EMA50")
    ema200 = indicators.get("EMA200")
    close = data.close

    if not all(v is not None for v in [ema20, ema50, close]):
        return "UNKNOWN"

    if close > ema20 > ema50:
        if ema200 is not None and ema50 > ema200:
            return "STRONG_UPTREND"
        return "UPTREND"
    elif close < ema20 < ema50:
        if ema200 is not None and ema50 < ema200:
            return "STRONG_DOWNTREND"
        return "DOWNTREND"
    return "SIDEWAYS"


def _extract_key_levels(data: MarketData) -> dict:
    """Extract support/resistance levels from pivot points."""
    ind = data.indicators
    levels = {}
    for key in ["Pivot.M.Classic.S1", "Pivot.M.Classic.S2", "Pivot.M.Classic.S3",
                 "Pivot.M.Classic.R1", "Pivot.M.Classic.R2", "Pivot.M.Classic.R3",
                 "Pivot.M.Classic.Middle"]:
        val = ind.get(key)
        if val is not None:
            short_key = key.split(".")[-1]
            if short_key == "Middle":
                short_key = "Pivot"
            levels[short_key] = round(val, 4)
    return levels


def analyze(data: MarketData) -> AnalysisResult:
    """Run technical analysis on collected market data.

    Args:
        data: MarketData from TradingView collector.

    Returns:
        AnalysisResult with aggregated signals.
    """
    summary = data.summary
    osc = data.oscillators
    ma = data.moving_averages

    summary_rec = summary.get("RECOMMENDATION", "NEUTRAL")
    osc_rec = osc.get("RECOMMENDATION", "NEUTRAL")
    ma_rec = ma.get("RECOMMENDATION", "NEUTRAL")

    osc_counts = osc.get("COMPUTE", {})
    ma_counts = ma.get("COMPUTE", {})

    return AnalysisResult(
        symbol=data.symbol,
        name=data.name,
        price=data.close,
        change_pct=data.change_pct,
        summary_recommendation=summary_rec,
        summary_score=SIGNAL_SCORE.get(summary_rec, 0),
        oscillator_recommendation=osc_rec,
        oscillator_buy=osc_counts.get("BUY", 0),
        oscillator_sell=osc_counts.get("SELL", 0),
        oscillator_neutral=osc_counts.get("NEUTRAL", 0),
        ma_recommendation=ma_rec,
        ma_buy=ma_counts.get("BUY", 0),
        ma_sell=ma_counts.get("SELL", 0),
        ma_neutral=ma_counts.get("NEUTRAL", 0),
        key_levels=_extract_key_levels(data),
        trend=_detect_trend(data),
    )


def analyze_multiple(
    market_data: dict[str, MarketData],
) -> dict[str, AnalysisResult]:
    """Analyze multiple symbols."""
    return {key: analyze(data) for key, data in market_data.items()}
