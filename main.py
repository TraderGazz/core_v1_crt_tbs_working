# main.py

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import MetaTrader5 as mt5_lib

from scheduler.scheduler import Scheduler
from fetchers.mt5_fetcher import MT5Fetcher
from fetchers.bybit_fetcher import BybitFetcher
from telegram.sender import TelegramSender
from config.strategy_profiles import STRATEGY_PROFILES

print("=== MAIN STARTED ===")

# ============================================================
# STRATEGY PROFILE
# ============================================================
ACTIVE_PROFILE_NAME = "swing_h4_m5"
PROFILE = STRATEGY_PROFILES[ACTIVE_PROFILE_NAME]

HTF_NAME = PROFILE["HTF"]
LTF_NAME = PROFILE["LTF"]

print(f"[MODE] {HTF_NAME} → {LTF_NAME}")

# ============================================================
# TIMEFRAMES
# ============================================================
MT5_TIMEFRAMES = {
    "M1": mt5_lib.TIMEFRAME_M1,
    "M5": mt5_lib.TIMEFRAME_M5,
    "M15": mt5_lib.TIMEFRAME_M15,
    "H1": mt5_lib.TIMEFRAME_H1,
    "H4": mt5_lib.TIMEFRAME_H4,
    "D1": mt5_lib.TIMEFRAME_D1,
}

HTF = MT5_TIMEFRAMES[HTF_NAME]
LTF = MT5_TIMEFRAMES[LTF_NAME]

# ============================================================
# FETCHERS
# ============================================================
mt5 = MT5Fetcher()
bybit = BybitFetcher()

# ============================================================
# TELEGRAM
# ============================================================
BOT_TOKEN = "8133810265:AAGEgpSykMU7TxoTj1st0DDAzM2wjHfX40w"
CHAT_ID = 7277187002

sender = TelegramSender(
    bot_token=BOT_TOKEN,
    chat_id=CHAT_ID,
)

# ============================================================
# PAIRS
# ============================================================
FOREX_PAIRS = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "USDCHF",
    "AUDUSD",
    "USDCAD",
    "NZDUSD",
    "XAUUSD",
]

CRYPTO_PAIRS = [
    # "BTCUSDT",
    # "ETHUSDT",
]

# ============================================================
# SYMBOL CONFIG
# ============================================================
symbols = []

for pair in FOREX_PAIRS:
    symbols.append({
        "symbol": pair,
        "market": "forex",
        "fetch_htf": lambda s, tf=HTF: mt5.fetch(s, tf),
        "fetch_ltf": lambda s, tf=LTF: mt5.fetch(s, tf),
    })

for pair in CRYPTO_PAIRS:
    symbols.append({
        "symbol": pair,
        "market": "crypto",
        "fetch_htf": lambda s, tf=HTF: bybit.fetch(s, tf),
        "fetch_ltf": lambda s, tf=LTF: bybit.fetch(s, tf),
    })

print(f"Loaded symbols: {len(symbols)}")

# ============================================================
# SCHEDULER
# ============================================================
scheduler = Scheduler(
    symbols=symbols,
    sender=sender,
    tick_seconds=60,
)

scheduler.run()
