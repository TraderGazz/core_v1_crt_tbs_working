# strategy/tbs_entry.py

from dataclasses import dataclass
from typing import Optional, List
from time import time

from data.models import Candle, CRTSetup


@dataclass
class TBSState:
    sweep_done: bool = False


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


def process_tbs(
    setup: CRTSetup,
    candles_m1: List[Candle],
    state: TBSState,
) -> Optional[Signal]:
    """
    HARD TEST VERSION.
    Если эта функция вызывается — она ВСЕГДА возвращает Signal.
    """

    print("[TBS] process_tbs CALLED")

    if setup.used:
        print("[TBS] setup already used")
        return None

    if len(candles_m1) < 2:
        print("[TBS] not enough candles")
        return None

    candle = candles_m1[-2]

    entry = candle.close
    sl = entry - 0.001
    tp1 = entry + 0.001
    tp2 = entry + 0.002

    setup.used = True

    print("[TBS] SIGNAL CREATED")

    return Signal(
        id=f"{setup.id}_{candle.timestamp}",
        symbol=setup.symbol,
        market=setup.market,
        direction=setup.direction,
        timeframe=f"{setup.htf} → {setup.ltf}",
        entry=entry,
        stop_loss=sl,
        tp1=tp1,
        tp2=tp2,
        rr_tp1=1.0,
        rr_tp2=2.0,
        crt_level=setup.level,
        sweep_price=sl,
        created_at=candle.timestamp,
        explanation="HARD TEST SIGNAL",
    )
