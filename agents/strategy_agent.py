import pandas as pd
import numpy as np
from strategies.strategy_registry import StrategyRegistry
from filelock import FileLock
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StrategyAgent:
    def __init__(self, data_file):
        """
        Initialize StrategyAgent with a CSV file path.
        Args:
            data_file: Path to CSV file with price data
        """
        self.data_file = data_file
        self.df = self.load_from_csv()
        self.positions = {}  # Store open positions: {entry_id: (quantity, entry_price)}
        self.completed_positions = []  # Store completed positions: [(entry_id, quantity, entry_price, exit_price, profit_loss)]
        self.output_dir = "data/processed"

    def load_from_csv(self):
        """
        Load data from CSV file.
        Returns:
            pandas.DataFrame: Data from CSV
        """
        lock = FileLock(f"{self.data_file}.lock")
        with lock:
            if os.path.exists(self.data_file):
                df = pd.read_csv(self.data_file, parse_dates=['open_time'])
                logger.info(f"Loaded data from {self.data_file}")
                return df
            raise ValueError(f"No data file found at {self.data_file}")

    def save_to_csv(self, df, symbol, interval, suffix="strategy"):
        """
        Save DataFrame to CSV with file locking.
        Args:
            df: DataFrame to save
            symbol: Trading pair symbol
            interval: Time interval
            suffix: Suffix for output file name
        """
        os.makedirs(self.output_dir, exist_ok=True)
        output_file = os.path.join(self.output_dir, f"{symbol}_{interval}_{suffix}.csv")
        lock = FileLock(f"{output_file}.lock")
        with lock:
            df.to_csv(output_file, index=False)
            logger.info(f"Saved data to {output_file}")

    def apply_strategy(self, strategy_name, symbol="BTCUSDT", interval="1h", **kwargs):
        """Apply the specified strategy and save results to CSV."""
        if strategy_name.lower() == "ema_crossover":
            calc_df = self.ema_crossover_strategy(**kwargs)
            self.save_to_csv(calc_df, symbol, interval, suffix="strategy")
            return calc_df
        else:
            raise ValueError(f"Strategy '{strategy_name}' not supported.")

    def ema_crossover_strategy(self, fast_length=9, slow_length=21, use_ha_df=False, ha_file=None, symbol="BTCUSDT", interval="1h"):
        """
        EMA crossover strategy with FIFO and profit/loss tracking.
        Args:
            fast_length: Period for fast EMA
            slow_length: Period for slow EMA
            use_ha_df: If True, use ha_df for calculations
            ha_file: Path to Heikin Ashi CSV file (optional)
            symbol: Trading pair symbol
            interval: Time interval
        Returns:
            DataFrame with strategy signals and position details
        """
        calc_df = self.load_from_csv() if not use_ha_df else self.load_from_csv(ha_file)
        calc_df['fast_ema'] = calc_df['close' if not use_ha_df else 'ha_close'].ewm(span=fast_length, adjust=False).mean()
        calc_df['slow_ema'] = calc_df['close' if not use_ha_df else 'ha_close'].ewm(span=slow_length, adjust=False).mean()
        calc_df['signal'] = 0
        calc_df['signal'] = np.where(calc_df['fast_ema'] > calc_df['slow_ema'], 1, np.where(calc_df['fast_ema'] < calc_df['slow_ema'], -1, 0))
        calc_df['position_change'] = calc_df['signal'].diff().fillna(0)
        calc_df['position'] = 0  # Initialize position column
        calc_df['entry_id'] = None  # New column to store entry IDs

        entry_id_counter = 1
        for index, row in calc_df.iterrows():
            if row['position_change'] == 2:  # Buy signal
                entry_id = f"#{entry_id_counter:06d}"
                entry_price = row['close' if not use_ha_df else 'ha_close']
                self.positions[entry_id] = (100, entry_price)  # Default quantity of 100
                calc_df.loc[index, 'position'] = 1  # Mark as open long position
                calc_df.loc[index, 'entry_id'] = entry_id  # Store entry ID
                entry_id_counter += 1
            elif row['position_change'] == -2:  # Sell signal
                if self.positions:
                    total_exit_quantity = 100  # Default exit quantity
                    remaining_exit = total_exit_quantity
                    while remaining_exit > 0 and self.positions:
                        earliest_entry_id = min(self.positions.keys())
                        quantity, entry_price = self.positions[earliest_entry_id]
                        exit_quantity = min(remaining_exit, quantity)
                        exit_price = row['close' if not use_ha_df else 'ha_close']
                        profit_loss = exit_quantity * (exit_price - entry_price)
                        self.completed_positions.append((earliest_entry_id, exit_quantity, entry_price, exit_price, profit_loss))
                        calc_df.loc[index, 'position'] = -1  # Mark as exit
                        calc_df.loc[index, 'entry_id'] = earliest_entry_id  # Use exiting entry ID
                        if quantity == exit_quantity:
                            del self.positions[earliest_entry_id]
                        else:
                            self.positions[earliest_entry_id] = (quantity - exit_quantity, entry_price)
                            new_id = f"{earliest_entry_id}a"
                            self.positions[new_id] = (quantity - exit_quantity, entry_price)
                        remaining_exit -= exit_quantity

        calc_df['open_positions'] = [list(self.positions.keys()) if self.positions else [] for _ in range(len(calc_df))]
        calc_df['completed_positions'] = [self.completed_positions.copy() for _ in range(len(calc_df))]
        self.save_to_csv(calc_df, symbol, interval, suffix="strategy")
        return calc_df