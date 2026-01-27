from fetchers.mt5_fetcher import MT5Fetcher

mt5 = MT5Fetcher()

pairs = ["EURUSD", "GBPUSD", "USDJPY", "USDCAD", "XAUUSD"]

for p in pairs:
    h1 = mt5.fetch_h1(p)
    m1 = mt5.fetch_m1(p)
    print(p, "H1:", len(h1), "M1:", len(m1))
