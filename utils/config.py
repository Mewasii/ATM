import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
    DEFAULT_SYMBOL = "BTCUSDT"  # Default trading pair
    DEFAULT_INTERVAL = "1h"     # Default time interval