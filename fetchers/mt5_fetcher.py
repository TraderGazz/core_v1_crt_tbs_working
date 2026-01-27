# fetchers/mt5_fetcher.py

import MetaTrader5 as mt5
from data.models import Candle


class MT5Fetcher:
    def __init__(self):
        if not mt5.initialize():
            raise RuntimeError("MT5 initialize failed")

        info = mt5.terminal_info()
        print(f"[MT5] Connected: {info.name} | build {info.build}")

        # кэш доступных символов
        self.symbols = {s.name: s for s in mt5.symbols_get()}

    def _resolve_symbol(self, symbol: str) -> str:
        # 1️⃣ точное совпадение
        if symbol in self.symbols:
            return symbol

        # 2️⃣ начинается с имени (EURUSD → EURUSDm)
        for name in self.symbols:
            if name.startswith(symbol):
                return name

        # 3️⃣ содержит имя (на всякий случай)
        for name in self.symbols:
            if symbol in name:
                return name

        raise RuntimeError(f"MT5 symbol not found: {symbol}")

    def fetch(self, symbol: str, timeframe, limit: int = 300):
        real_symbol = self._resolve_symbol(symbol)

        info = mt5.symbol_info(real_symbol)
        if info is None:
            raise RuntimeError(f"MT5 symbol_info failed: {real_symbol}")

        if not info.visible:
            mt5.symbol_select(real_symbol, True)

        rates = mt5.copy_rates_from_pos(real_symbol, timeframe, 0, limit)
        if rates is None or len(rates) == 0:
            return []

        candles = []
        for r in rates:
            candles.append(
                Candle(
                    timestamp=int(r["time"]),
                    open=r["open"],
                    high=r["high"],
                    low=r["low"],
                    close=r["close"],
                    volume=r["tick_volume"],
                )
            )

        return candles
