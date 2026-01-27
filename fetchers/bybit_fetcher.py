# fetchers/bybit_fetcher.py
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from data.models import Candle


class BybitFetcher:
    def __init__(self):
        self.base_url = "https://api.bybit.com"
        self.session = requests.Session()

        retry = Retry(
            total=5,                  # общее число повторов
            connect=5,
            read=5,
            backoff_factor=0.6,        # 0.6s, 1.2s, 2.4s...
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=50, pool_maxsize=50)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch_h1(self, symbol: str):
        # H1 можно брать меньше, чем 500 — тебе не надо столько
        return self._fetch(symbol, interval="60", limit=200)

    def fetch_m1(self, symbol: str):
        return self._fetch(symbol, interval="1", limit=300)

    def _fetch(self, symbol: str, interval: str, limit: int):
        url = f"{self.base_url}/v5/market/kline"
        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }

        # timeout лучше tuple: (connect_timeout, read_timeout)
        # read_timeout увеличиваем, чтобы не ловить обрыв на загруженной сети
        r = self.session.get(url, params=params, timeout=(5, 25))
        data = r.json()

        if not data.get("ok", True) and data.get("retCode", 0) != 0:
            # Bybit иногда возвращает retCode вместо ok
            raise RuntimeError(f"Bybit error: {data}")

        result = data.get("result", {})
        klines = result.get("list", []) or result.get("data", []) or []

        candles = []
        # Bybit часто отдаёт список строк: [openTime, open, high, low, close, volume, turnover]
        for k in klines:
            ts = int(k[0]) // 1000  # ms -> sec
            o = float(k[1]); h = float(k[2]); l = float(k[3]); c = float(k[4])
            v = float(k[5]) if len(k) > 5 else None
            candles.append(Candle(timestamp=ts, open=o, high=h, low=l, close=c, volume=v))

        candles.sort(key=lambda x: x.timestamp)
        return candles
