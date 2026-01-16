# scheduler/scheduler.py

import time as time_module
from typing import Dict, List

from data.models import Candle, CRTSetup
from strategy.crt_context import detect_crt
from strategy.tbs_entry import process_tbs, TBSState, Signal


# =========================
# IMPORT DIAGNOSTICS
# =========================
print("[IMPORT] scheduler file:", __file__)
print("[IMPORT] process_tbs module:", process_tbs.__module__)
print("[IMPORT] process_tbs file:", process_tbs.__code__.co_filename)


class Scheduler:
    """
    Signal-only scheduler.
    CRT (H1) -> TBS (M1) -> Signal
    """

    def __init__(self, symbols: List[dict], tick_seconds: int = 2):
        self.symbols = symbols
        self.tick_seconds = tick_seconds

        self.active_setups: Dict[str, CRTSetup] = {}
        self.tbs_states: Dict[str, TBSState] = {}

    def run(self):
        print("=== SCHEDULER RUNNING ===")
        print("SYMBOLS =", self.symbols)

        while True:
            for cfg in self.symbols:
                symbol = cfg["symbol"]
                market = cfg["market"]

                candles_h1 = cfg["fetch_h1"](symbol)
                candles_m1 = cfg["fetch_m1"](symbol)

                if not candles_h1 or not candles_m1:
                    print("[SCHEDULER] empty candles")
                    continue

                self._process_symbol(
                    symbol=symbol,
                    market=market,
                    candles_h1=candles_h1,
                    candles_m1=candles_m1,
                )

            time_module.sleep(self.tick_seconds)

    def _process_symbol(
        self,
        symbol: str,
        market: str,
        candles_h1: List[Candle],
        candles_m1: List[Candle],
    ):
        print(f"[SCHEDULER] processing {symbol}")

        # =========================
        # 1) CRT
        # =========================
        if symbol not in self.active_setups:
            print("[SCHEDULER] detecting CRT...")
            setup = detect_crt(
                candles_h1=candles_h1,
                symbol=symbol,
                market=market,
            )
            if setup:
                self.active_setups[symbol] = setup
                self.tbs_states[symbol] = TBSState()
                print(f"[CRT] {symbol} {setup.direction} level={setup.level}")
            else:
                print("[SCHEDULER] no CRT")
                return

        # =========================
        # 2) TBS
        # =========================
        setup = self.active_setups[symbol]
        state = self.tbs_states[symbol]

        print("[SCHEDULER] about to call process_tbs")

        signal = process_tbs(
            setup=setup,
            candles_m1=candles_m1,
            state=state,
        )

        if isinstance(signal, Signal):
            print("[SCHEDULER] SIGNAL RECEIVED")
            self.on_signal(signal)

            # cleanup
            self.active_setups.pop(symbol, None)
            self.tbs_states.pop(symbol, None)
            return

        # =========================
        # 3) CLEANUP
        # =========================
        if setup.used or int(time_module.time()) > setup.expires_at:
            print("[SCHEDULER] cleanup expired/used setup")
            self.active_setups.pop(symbol, None)
            self.tbs_states.pop(symbol, None)

    def on_signal(self, signal: Signal):
        print("====== SIGNAL ======")
        print(f"{signal.symbol} • {signal.market} • {signal.direction} • {signal.timeframe}")
        print(f"Entry: {signal.entry}")
        print(f"SL:    {signal.stop_loss}")
        print(f"TP1:   {signal.tp1}")
        print(f"TP2:   {signal.tp2}")
        print(signal.explanation)
        print("====================")
