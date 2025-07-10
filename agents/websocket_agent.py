import asyncio
import websockets
import json
import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebSocketAgent:
    def __init__(self, symbol, interval):
        """
        Initialize WebSocketAgent for real-time kline data.
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            interval: Kline interval (e.g., 1h)
        """
        self.symbol = symbol.lower()
        self.interval = interval
        self.running = False
        self.data = pd.DataFrame(columns=['open_time', 'open', 'high', 'low', 'close', 'volume'])
        self.websocket_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@kline_{self.interval}"

    async def connect(self):
        """
        Connect to Binance WebSocket and process kline data.
        """
        self.running = True
        while self.running:
            try:
                async with websockets.connect(self.websocket_url) as websocket:
                    logger.info(f"Connected to WebSocket for {self.symbol} at {self.interval}")
                    while self.running:
                        message = await websocket.recv()
                        data = json.loads(message)
                        if 'k' in data:
                            kline = data['k']
                            if kline['x']:  # Only process closed klines
                                df = pd.DataFrame([{
                                    'open_time': pd.to_datetime(kline['t'], unit='ms'),
                                    'open': float(kline['o']),
                                    'high': float(kline['h']),
                                    'low': float(kline['l']),
                                    'close': float(kline['c']),
                                    'volume': float(kline['v'])
                                }])
                                self.data = pd.concat([self.data, df]).drop_duplicates(subset=['open_time'], keep='last')
                                logger.info(f"Received kline for {self.symbol} at {kline['t']}")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await asyncio.sleep(5)  # Wait before reconnecting

    def stop(self):
        """Stop the WebSocket connection."""
        self.running = False
        logger.info("WebSocket stopped")

    def get_data(self):
        """
        Get the current kline data.
        Returns:
            pandas.DataFrame: Kline data
        """
        return self.data.copy()