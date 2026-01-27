# data/models.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None


@dataclass
class CRTSetup:
    id: str
    symbol: str
    market: str            # "crypto" | "forex"

    direction: str         # "BUY" | "SELL"
    htf: str               # "H1"
    ltf: str               # "M1"

    crt_timestamp: int
    crt_high: float
    crt_low: float
    crt_range: float
    atr_h1: float

    level: float

    expires_at: int
    used: bool = False

from dataclasses import dataclass

@dataclass
class ActiveTrade:
    symbol: str
    market: str
    direction: str

    entry: float
    stop_loss: float
    tp1: float
    tp2: float

    opened_at: int
    status: str  # "open" | "closed"
