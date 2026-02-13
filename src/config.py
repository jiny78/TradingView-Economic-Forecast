"""Application configuration."""

import os
from dotenv import load_dotenv

load_dotenv()

# Supported symbols for analysis
SYMBOLS = {
    "indices": {
        "SPX": ("SP:SPX", "S&P 500"),
        "DJI": ("DJ:DJI", "Dow Jones Industrial"),
        "IXIC": ("NASDAQ:IXIC", "NASDAQ Composite"),
        "KOSPI": ("KRX:KOSPI", "KOSPI"),
        "KOSDAQ": ("KRX:KOSDAQ", "KOSDAQ"),
        "NI225": ("TVC:NI225", "Nikkei 225"),
        "HSI": ("TVC:HSI", "Hang Seng Index"),
    },
    "forex": {
        "EURUSD": ("FX_IDC:EURUSD", "EUR/USD"),
        "USDJPY": ("FX_IDC:USDJPY", "USD/JPY"),
        "USDKRW": ("FX_IDC:USDKRW", "USD/KRW"),
        "GBPUSD": ("FX_IDC:GBPUSD", "GBP/USD"),
    },
    "crypto": {
        "BTCUSD": ("BITSTAMP:BTCUSD", "Bitcoin"),
        "ETHUSD": ("BITSTAMP:ETHUSD", "Ethereum"),
    },
    "commodities": {
        "GOLD": ("TVC:GOLD", "Gold"),
        "SILVER": ("TVC:SILVER", "Silver"),
        "USOIL": ("TVC:USOIL", "WTI Crude Oil"),
    },
}

# TradingView screener mappings
SCREENER_MAP = {
    "SP": "america",
    "DJ": "america",
    "NASDAQ": "america",
    "NYSE": "america",
    "KRX": "korea",
    "TVC": "cfd",
    "FX_IDC": "forex",
    "BITSTAMP": "crypto",
    "BINANCE": "crypto",
}

# Technical analysis intervals
INTERVALS = ["1m", "5m", "15m", "1h", "4h", "1d", "1W", "1M"]
DEFAULT_INTERVAL = "1d"

# Forecast settings
FORECAST_DAYS = int(os.getenv("FORECAST_DAYS", "30"))
MODEL_LOOKBACK = int(os.getenv("MODEL_LOOKBACK", "60"))

# Flask settings
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
