# telegram/sender.py

import requests
from strategy.tbs_entry import Signal


class TelegramSender:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def send_trade_close(self, trade, reason: str):
        message = f"""
🔴 <b>TRADE CLOSED</b>

📌 <b>{trade.symbol}</b> • <b>{trade.direction}</b>
Reason: <b>{reason}</b>

Entry → {trade.entry}
SL    → {trade.stop_loss}
TP2   → {trade.tp2}
""".strip()

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
        }

        r = requests.post(self.api_url, json=payload, timeout=10)
        print("[TG CLOSE]", r.status_code, r.text)

    def send_signal(self, signal: Signal):
        message = self._format_signal(signal)
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        r = requests.post(self.api_url, json=payload, timeout=10)

        print("[TG] status:", r.status_code)
        print("[TG] response:", r.text)

    def _format_signal(self, signal: Signal) -> str:
        # Без округления: ровно как в логах (str(float))
        return f"""
🟢 <b>CRT + TBS SIGNAL</b>

📌 <b>{signal.symbol}</b> • <b>{signal.direction}</b>
⏱ <b>{signal.timeframe}</b>

🎯 <b>Entry</b> → {signal.entry}
🛑 <b>SL</b>    → {signal.stop_loss}
🎯 <b>TP1</b>   → {signal.tp1}
🎯 <b>TP2</b>   → {signal.tp2}

📊 <b>Risk / Reward</b>
TP1 ≈ 1 : 1
TP2 ≈ 1 : 2

🧠 <b>Описание</b>
{signal.explanation}

⚠️ <i>Не является инвестиционной рекомендацией</i>
""".strip()
