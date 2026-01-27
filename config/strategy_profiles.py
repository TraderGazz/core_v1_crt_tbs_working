# config/strategy_profiles.py

STRATEGY_PROFILES = {
    "swing_h4_m5": {
        "HTF": "H4",
        "LTF": "M5",

        "CRT_ATR_PERIOD": 14,
        "CRT_RANGE_MULT": 2.5,
        "CRT_MAX_RANGE_MULT": 6.0,
        "CRT_BODY_RATIO": 0.6,
        "CRT_TTL_HOURS": 24,

        "TBS_MAX_MINUTES_AFTER_SWEEP": 60,
        "TBS_SL_ATR_BUFFER_MULT": 0.2,
        "TBS_MAX_RISK_ATR_H1_MULT": 3.0,
    }
}
