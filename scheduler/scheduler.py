# scheduler/scheduler.py

import time
from typing import Dict, List

from data.models import Candle, CRTSetup, ActiveTrade
from strategy.crt_context import detect_crt
from strategy.tbs_entry import process_tbs, TBSState, Signal


class Scheduler:
    def __init__(self, symbols: List[dict], sender, tick_seconds: int = 60):
        self.symbols = symbols
        self.tick_seconds = tick_seconds

        self.active_setups: Dict[str, CRTSetup] = {}
        self.tbs_states: Dict[str, TBSState] = {}
        self.active_trades: Dict[str, ActiveTrade] = {}

        self.sender = sender  # ← ВАЖНО: sender приходит извне

    def run(self):
        print("=== SCHEDULER RUNNING ===")
        while True:
            for cfg in self.symbols:
                symbol = cfg["symbol"]
                market = cfg["market"]

                try:
                    candles_htf = cfg["fetch_htf"](symbol)
                    candles_ltf = cfg["fetch_ltf"](symbol)
                except Exception as e:
                    print(f"[FETCH ERROR] {symbol}: {e}")
                    continue

                if not candles_htf or not candles_ltf:
                    continue

                self._process_symbol(symbol, market, candles_htf, candles_ltf)

            time.sleep(self.tick_seconds)

    def _process_symbol(
        self,
        symbol: str,
        market: str,
        candles_htf: List[Candle],
        candles_ltf: List[Candle],
    ):
        # ===== ACTIVE TRADE =====
        if symbol in self.active_trades:
            self._update_trade(symbol, candles_ltf)
            return

        # ===== CRT =====
        if symbol not in self.active_setups:
            setup = detect_crt(candles_htf, symbol, market)
            if setup:
                self.active_setups[symbol] = setup
                self.tbs_states[symbol] = TBSState()
                print(f"[CRT] {symbol} {setup.direction} level={setup.level}")

        # ===== TBS =====
        if symbol in self.active_setups:
            setup = self.active_setups[symbol]
            state = self.tbs_states[symbol]

            signal = process_tbs(setup, candles_ltf, state)
            if isinstance(signal, Signal):
                self.on_signal(signal)
                self.active_setups.pop(symbol, None)
                self.tbs_states.pop(symbol, None)
                return

            if setup.used or int(time.time()) > setup.expires_at:
                self.active_setups.pop(symbol, None)
                self.tbs_states.pop(symbol, None)

    def _update_trade(self, symbol: str, candles_ltf: List[Candle]):
        if not candles_ltf:
            return

        trade = self.active_trades[symbol]
        price = candles_ltf[-1].close

        if trade.direction == "BUY":
            if price <= trade.stop_loss:
                self._close_trade(symbol, "STOP LOSS")
            elif price >= trade.tp2:
                self._close_trade(symbol, "TAKE PROFIT")
        else:
            if price >= trade.stop_loss:
                self._close_trade(symbol, "STOP LOSS")
            elif price <= trade.tp2:
                self._close_trade(symbol, "TAKE PROFIT")

    def _close_trade(self, symbol: str, reason: str):
        trade = self.active_trades.pop(symbol)
        print(f"[TRADE CLOSED] {symbol} {reason}")
        self.sender.send_trade_close(trade, reason)

    def on_signal(self, signal: Signal):
        print("====== SIGNAL ======")
        print(f"{signal.symbol} • {signal.market} • {signal.direction} • {signal.timeframe}")
        print(f"Entry: {signal.entry}")
        print(f"SL:    {signal.stop_loss}")
        print(f"TP1:   {signal.tp1}")
        print(f"TP2:   {signal.tp2}")
        print(signal.explanation)
        print("====================")

        self.sender.send_signal(signal)

        self.active_trades[signal.symbol] = ActiveTrade(
            symbol=signal.symbol,
            market=signal.market,
            direction=signal.direction,
            entry=signal.entry,
            stop_loss=signal.stop_loss,
            tp1=signal.tp1,
            tp2=signal.tp2,
            opened_at=signal.created_at,
            status="open",
        )
