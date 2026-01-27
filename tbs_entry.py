# strategy/tbs_entry.py

from dataclasses import dataclass
from typing import Optional, List
from time import time

from data.models import Candle, CRTSetup
from config.strategy_profiles import STRATEGY_PROFILES
STRATEGY_PROFILE = STRATEGY_PROFILES["swing_h4_m5"]



@dataclass
class TBSState:
    sweep_done: bool = False
    sweep_price: Optional[float] = None
    sweep_timestamp: Optional[int] = None


@dataclass
class Signal:
    id: str
    symbol: str
    market: str
    direction: str
    timeframe: str
    entry: float
    stop_loss: float
    tp1: float
    tp2: float
    rr_tp1: float
    rr_tp2: float
    crt_level: float
    sweep_price: float
    created_at: int
    explanation: str


def calculate_atr(candles: List[Candle], period: int) -> float:
    if len(candles) < period + 1:
        return 0.0

    trs = []
    for i in range(1, period + 1):
        high = candles[-i].high
        low = candles[-i].low
        prev_close = candles[-i - 1].close

        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close),
        )
        trs.append(tr)

    return sum(trs) / len(trs)


def process_tbs(
    setup: CRTSetup,
    candles_ltf: List[Candle],
    state: TBSState,
) -> Optional[Signal]:
    if setup.used:
        return None

    if int(time()) > setup.expires_at:
        return None

    if len(candles_ltf) < 6:
        return None

    last_closed = candles_ltf[-2]

    # ===== SWEEP =====
    if not state.sweep_done:
        lookback = candles_ltf[-10:-1]
        for c in lookback:
            if setup.direction == "BUY" and c.low < setup.crt_low:
                state.sweep_done = True
                state.sweep_price = c.low
                state.sweep_timestamp = c.timestamp
                break
            if setup.direction == "SELL" and c.high > setup.crt_high:
                state.sweep_done = True
                state.sweep_price = c.high
                state.sweep_timestamp = c.timestamp
                break

        if not state.sweep_done:
            return None

    if last_closed.timestamp - state.sweep_timestamp > STRATEGY_PROFILE["TBS_MAX_MINUTES_AFTER_SWEEP"] * 60:
        return None

    # ===== RETURN =====
    if setup.direction == "BUY":
        if last_closed.close <= setup.crt_low:
            return None
    else:
        if last_closed.close >= setup.crt_high:
            return None

    entry = last_closed.close

    atr_ltf = calculate_atr(candles_ltf[:-1], STRATEGY_PROFILE["CRT_ATR_PERIOD"])
    buffer = atr_ltf * STRATEGY_PROFILE["TBS_SL_ATR_BUFFER_MULT"]

    if setup.direction == "BUY":
        sl = state.sweep_price - buffer
        risk = entry - sl
        tp1 = entry + risk * 2
        tp2 = entry + risk * 4
    else:
        sl = state.sweep_price + buffer
        risk = sl - entry
        tp1 = entry - risk * 2
        tp2 = entry - risk * 4

    if risk <= 0:
        return None

    if risk > setup.atr_h1 * STRATEGY_PROFILE["TBS_MAX_RISK_ATR_H1_MULT"]:
        return None

    setup.used = True

    return Signal(
        id=f"{setup.id}_{last_closed.timestamp}",
        symbol=setup.symbol,
        market=setup.market,
        direction=setup.direction,
        timeframe=f"{setup.htf} → {setup.ltf}",
        entry=entry,
        stop_loss=sl,
        tp1=tp1,
        tp2=tp2,
        rr_tp1=2.0,
        rr_tp2=4.0,
        crt_level=setup.level,
        sweep_price=state.sweep_price,
        created_at=last_closed.timestamp,
        explanation="CRT (HTF) → sweep (LTF) → return → entry on close.",
    )
