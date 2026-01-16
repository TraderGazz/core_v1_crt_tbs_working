# strategy/crt_context.py

from typing import List, Optional
from time import time

from data.models import Candle, CRTSetup
from config import (
    CRT_HTF,
    CRT_LTF,
    CRT_ATR_PERIOD,
    CRT_RANGE_MULT,
    CRT_MAX_RANGE_MULT,
    CRT_BODY_RATIO,
    CRT_TTL_HOURS,
)


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


def is_impulse_candle(candle: Candle, atr: float) -> bool:
    if atr <= 0:
        return False

    candle_range = candle.high - candle.low
    if candle_range < atr * CRT_RANGE_MULT:
        return False

    # анти-новостной фильтр
    if candle_range > atr * CRT_MAX_RANGE_MULT:
        return False

    body = abs(candle.close - candle.open)
    if candle_range <= 0:
        return False

    if body / candle_range < CRT_BODY_RATIO:
        return False

    return True


def detect_crt(
    candles_h1: List[Candle],
    symbol: str,
    market: str,
) -> Optional[CRTSetup]:
    # Нужно: ATR_PERIOD+1 свеча для ATR и +1 чтобы взять последнюю закрытую (-2)
    if len(candles_h1) < CRT_ATR_PERIOD + 2:
        return None

    # последняя закрытая свеча
    crt_candle = candles_h1[-2]

    # ATR считаем по закрытым свечам (без самой “текущей”)
    atr = calculate_atr(candles_h1[:-1], CRT_ATR_PERIOD)
    if atr <= 0:
        return None

    if not is_impulse_candle(crt_candle, atr):
        return None

    direction = "BUY" if crt_candle.close > crt_candle.open else "SELL"
    level = crt_candle.low if direction == "BUY" else crt_candle.high

    expires_at = crt_candle.timestamp + CRT_TTL_HOURS * 3600

    return CRTSetup(
        id=f"{symbol}_{crt_candle.timestamp}",
        symbol=symbol,
        market=market,

        direction=direction,
        htf=CRT_HTF,
        ltf=CRT_LTF,

        crt_timestamp=crt_candle.timestamp,
        crt_high=crt_candle.high,
        crt_low=crt_candle.low,
        crt_range=crt_candle.high - crt_candle.low,
        atr_h1=atr,

        level=level,
        expires_at=expires_at,
        used=False,
    )
