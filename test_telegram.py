import requests

BOT_TOKEN = "8133810265:AAEJ_cIC10-MP1YwaY-MWD0uEN3l2S34bGA"
CHAT_ID = "7277187002"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": "✅ Тестовое сообщение: Telegram-бот подключён",
}

r = requests.post(url, json=payload, timeout=10)
print(r.status_code)
print(r.text)
