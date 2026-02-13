"""ML-based economic forecast module.

Uses technical indicator features from TradingView to predict
short-term price direction and generate forecast signals.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

from src.data.collector import MarketData

logger = logging.getLogger(__name__)

# Feature keys extracted from TradingView indicators
FEATURE_KEYS = [
    "RSI", "RSI[1]",
    "Stoch.K", "Stoch.D",
    "CCI20", "CCI20[1]",
    "ADX", "ADX+DI", "ADX-DI",
    "AO", "AO[1]",
    "Mom", "Mom[1]",
    "MACD.macd", "MACD.signal",
    "BBPower",
    "EMA10", "EMA20", "EMA50", "EMA100", "EMA200",
    "SMA10", "SMA20", "SMA50", "SMA100", "SMA200",
    "Rec.WR", "Rec.Stoch.RSI",
]


@dataclass
class ForecastResult:
    """Prediction result for a single symbol."""

    symbol: str
    name: str
    current_price: float
    direction: str  # "UP", "DOWN", "NEUTRAL"
    confidence: float  # 0.0 ~ 1.0
    signal_strength: int  # -100 ~ 100
    factors: dict = field(default_factory=dict)

    @property
    def direction_kr(self) -> str:
        return {"UP": "상승", "DOWN": "하락", "NEUTRAL": "보합"}.get(
            self.direction, self.direction
        )

    @property
    def direction_emoji(self) -> str:
        return {"UP": "▲", "DOWN": "▼", "NEUTRAL": "━"}.get(
            self.direction, "?"
        )


def _extract_features(data: MarketData) -> np.ndarray | None:
    """Extract feature vector from MarketData indicators."""
    features = []
    for key in FEATURE_KEYS:
        val = data.indicators.get(key)
        if val is None:
            features.append(0.0)
        else:
            features.append(float(val))
    return np.array(features).reshape(1, -1)


def _rule_based_forecast(data: MarketData) -> ForecastResult:
    """Generate a rule-based forecast when ML data is insufficient."""
    ind = data.indicators
    score = 0
    factors = {}

    # RSI signal
    rsi = ind.get("RSI")
    if rsi is not None:
        if rsi < 30:
            score += 2
            factors["RSI"] = f"{rsi:.1f} (oversold - bullish)"
        elif rsi > 70:
            score -= 2
            factors["RSI"] = f"{rsi:.1f} (overbought - bearish)"
        elif rsi < 50:
            score -= 1
            factors["RSI"] = f"{rsi:.1f} (below midline)"
        else:
            score += 1
            factors["RSI"] = f"{rsi:.1f} (above midline)"

    # MACD signal
    macd = ind.get("MACD.macd")
    macd_signal = ind.get("MACD.signal")
    if macd is not None and macd_signal is not None:
        if macd > macd_signal:
            score += 2
            factors["MACD"] = "bullish crossover"
        else:
            score -= 2
            factors["MACD"] = "bearish crossover"

    # Moving average trend
    close = data.close
    ema20 = ind.get("EMA20")
    ema50 = ind.get("EMA50")
    if ema20 is not None and close:
        if close > ema20:
            score += 1
            factors["EMA20"] = "price above EMA20"
        else:
            score -= 1
            factors["EMA20"] = "price below EMA20"
    if ema50 is not None and close:
        if close > ema50:
            score += 1
            factors["EMA50"] = "price above EMA50"
        else:
            score -= 1
            factors["EMA50"] = "price below EMA50"

    # Stochastic
    stoch_k = ind.get("Stoch.K")
    stoch_d = ind.get("Stoch.D")
    if stoch_k is not None and stoch_d is not None:
        if stoch_k < 20 and stoch_k > stoch_d:
            score += 2
            factors["Stochastic"] = "oversold with bullish cross"
        elif stoch_k > 80 and stoch_k < stoch_d:
            score -= 2
            factors["Stochastic"] = "overbought with bearish cross"

    # ADX trend strength
    adx = ind.get("ADX")
    adx_plus = ind.get("ADX+DI")
    adx_minus = ind.get("ADX-DI")
    if adx is not None and adx_plus is not None and adx_minus is not None:
        if adx > 25:
            if adx_plus > adx_minus:
                score += 1
                factors["ADX"] = f"{adx:.1f} strong uptrend"
            else:
                score -= 1
                factors["ADX"] = f"{adx:.1f} strong downtrend"

    # CCI
    cci = ind.get("CCI20")
    if cci is not None:
        if cci < -100:
            score += 1
            factors["CCI"] = f"{cci:.1f} (oversold)"
        elif cci > 100:
            score -= 1
            factors["CCI"] = f"{cci:.1f} (overbought)"

    # Bollinger Bands
    bb_upper = ind.get("BB.upper")
    bb_lower = ind.get("BB.lower")
    if bb_upper is not None and bb_lower is not None and close:
        if close <= bb_lower:
            score += 1
            factors["BB"] = "at lower band (support)"
        elif close >= bb_upper:
            score -= 1
            factors["BB"] = "at upper band (resistance)"

    # TradingView summary
    summary = data.summary.get("RECOMMENDATION", "NEUTRAL")
    tv_score = {"STRONG_BUY": 3, "BUY": 1, "NEUTRAL": 0, "SELL": -1, "STRONG_SELL": -3}
    score += tv_score.get(summary, 0)
    factors["TV_Summary"] = summary

    # Determine direction
    max_possible = 16
    signal_strength = int(np.clip(score / max_possible * 100, -100, 100))

    if score >= 3:
        direction = "UP"
    elif score <= -3:
        direction = "DOWN"
    else:
        direction = "NEUTRAL"

    confidence = min(abs(score) / max_possible, 1.0)

    return ForecastResult(
        symbol=data.symbol,
        name=data.name,
        current_price=data.close,
        direction=direction,
        confidence=round(confidence, 3),
        signal_strength=signal_strength,
        factors=factors,
    )


def predict(data: MarketData) -> ForecastResult:
    """Generate a forecast for a single symbol.

    Uses rule-based analysis combining multiple TradingView
    indicators into a directional forecast.
    """
    return _rule_based_forecast(data)


def predict_multiple(
    market_data: dict[str, MarketData],
) -> dict[str, ForecastResult]:
    """Generate forecasts for multiple symbols."""
    return {key: predict(data) for key, data in market_data.items()}
