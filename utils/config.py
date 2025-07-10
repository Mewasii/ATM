import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BINANCE_API_KEY = os.getenv("fY5h0wvLb9zafn02LEjjguigAkm8FTMUVouCCTzVRoYcyNKRjLxPqKj5S5ntCtZW")
    BINANCE_API_SECRET = os.getenv("xSRXfUTJxNeHFOaXvrBPDCSXanb33PsLzIx3yUIF763Yc6n62SwDUqDqPihDMASM")
    DEFAULT_SYMBOL = "BTCUSDT"  # Default trading pair
    DEFAULT_INTERVAL = "1h"     # Default time interval
    RAW_DATA_DIR = "data/raw"
    PROCESSED_DATA_DIR = "data/processed"