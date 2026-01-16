# main.py

import time
from scheduler.scheduler import Scheduler
from data.models import Candle

print("=== MAIN STARTED ===")


# =========================
# HARD-CODED TEST FEED
# =========================

class HardTestFeed:
    """
    Отдаёт данные так, что:
    - CRT гарантирован
    - sweep был
    - return был
    - entry должен быть создан СРАЗУ
    """

    def get_h1(self, symbol):
        now = int(time.time())
        candles = []

        # 15 спокойных свечей
        price = 1.1000
        for i in range(15):
            candles.append(
                Candle(
                    timestamp=now - (20 - i) * 3600,
                    open=price,
                    high=price + 0.0010,
                    low=price - 0.0010,
                    close=price + 0.0003,
                )
            )

        # ЗАКРЫТАЯ ПОСЛЕДНЯЯ ОБЫЧНАЯ
        candles.append(
            Candle(
                timestamp=now - 2 * 3600,
                open=1.1000,
                high=1.1010,
                low=1.0995,
                close=1.1005,
            )
        )

        # CRT ИМПУЛЬС — ДОЛЖЕН БЫТЬ [-2]
        candles.append(
            Candle(
                timestamp=now - 3600,
                open=1.1005,
                high=1.1065,
                low=1.1005,
                close=1.1060,
            )
        )

        # формирующаяся
        last = candles[-1]
        candles.append(
            Candle(
                timestamp=last.timestamp + 3600,
                open=last.close,
                high=last.close,
                low=last.close,
                close=last.close,
            )
        )

        return candles


    def get_m1(self, symbol):
        now = int(time.time())

        candles = []

        # обычные
        for i in range(5):
            candles.append(
                Candle(
                    timestamp=now - (10 - i) * 60,
                    open=1.1040,
                    high=1.1042,
                    low=1.1038,
                    close=1.1040,
                )
            )

        # SWEEP
        candles.append(
            Candle(
                timestamp=now - 4 * 60,
                open=1.1040,
                high=1.1042,
                low=1.1000,      # ниже CRT low = 1.1005
                close=1.1008,
            )
        )

        # RETURN (ENTRY HERE)
        candles.append(
            Candle(
                timestamp=now - 3 * 60,
                open=1.1008,
                high=1.1030,
                low=1.1006,
                close=1.1020,    # закрылись выше CRT low
            )
        )

        # формирующаяся
        last = candles[-1]
        candles.append(
            Candle(
                timestamp=last.timestamp + 60,
                open=last.close,
                high=last.close,
                low=last.close,
                close=last.close,
            )
        )

        return candles


feed = HardTestFeed()

symbols = [
    {
        "symbol": "EURUSD",
        "market": "forex",
        "fetch_h1": feed.get_h1,
        "fetch_m1": feed.get_m1,
    }
]

scheduler = Scheduler(symbols=symbols, tick_seconds=9999)
scheduler.run()
