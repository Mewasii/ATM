import pandas as pd
from filelock import FileLock
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCalculationAgent:
    def __init__(self):
        """Initialize DataCalculationAgent with storage for original and calculated data."""
        self.original_data = None
        self.calculated_data = None
        self.output_dir = "data/processed"

    def load_from_csv(self, data_file):
        """
        Load data from CSV file.
        Args:
            data_file: Path to CSV file
        Returns:
            pandas.DataFrame: Data from CSV
        """
        lock = FileLock(f"{data_file}.lock")
        with lock:
            if os.path.exists(data_file):
                df = pd.read_csv(data_file, parse_dates=['open_time'])
                logger.info(f"Loaded data from {data_file}")
                return df
            raise ValueError(f"No data file found at {data_file}")

    def save_to_csv(self, df, symbol, interval, suffix="heikin_ashi"):
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

    def calculate_heikin_ashi(self, data_file, symbol="BTCUSDT", interval="1h"):
        """
        Calculate Heikin Ashi data from CSV file and save to CSV.
        Args:
            data_file: Path to CSV file with columns ['open_time', 'open', 'high', 'low', 'close']
            symbol: Trading pair symbol
            interval: Time interval
        Returns:
            DataFrame with Heikin Ashi data
        """
        df = self.load_from_csv(data_file)
        logger.info(f"Calculating Heikin Ashi with df columns: {df.columns.tolist()}")
        if not all(col in df.columns for col in ['open_time', 'open', 'high', 'low', 'close']):
            raise ValueError("DataFrame must have 'open_time', 'open', 'high', 'low', 'close' for Heikin Ashi")
        self.original_data = df.copy()
        try:
            if len(df) < 1:
                raise ValueError("DataFrame has fewer than 1 row, cannot calculate Heikin Ashi")
            ha_df = df.copy()
            # Initialize first row Heikin Ashi values
            ha_df['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
            ha_df.loc[ha_df.index[0], 'ha_open'] = (df['open'].iloc[0] + df['close'].iloc[0]) / 2
            ha_df.loc[ha_df.index[0], 'ha_high'] = ha_df[['high', 'ha_open', 'ha_close']].iloc[0].max()
            ha_df.loc[ha_df.index[0], 'ha_low'] = ha_df[['low', 'ha_open', 'ha_close']].iloc[0].min()
            # Calculate subsequent rows
            for i in range(1, len(df)):
                ha_df.loc[ha_df.index[i], 'ha_close'] = (df['open'].iloc[i] + df['high'].iloc[i] + df['low'].iloc[i] + df['close'].iloc[i]) / 4
                ha_df.loc[ha_df.index[i], 'ha_open'] = (ha_df['ha_open'].iloc[i-1] + ha_df['ha_close'].iloc[i-1]) / 2
                ha_df.loc[ha_df.index[i], 'ha_high'] = ha_df[['high', 'ha_open', 'ha_close']].iloc[i].max()
                ha_df.loc[ha_df.index[i], 'ha_low'] = ha_df[['low', 'ha_open', 'ha_close']].iloc[i].min()
            self.calculated_data = ha_df[['open_time', 'ha_open', 'ha_high', 'ha_low', 'ha_close', 'close']].fillna(0)
            if self.calculated_data.empty:
                logger.warning("Heikin Ashi data is empty after processing")
                self.calculated_data = ha_df[['open_time', 'ha_open', 'ha_high', 'ha_low', 'ha_close', 'close']].fillna(0)
            # Save to CSV
            self.save_to_csv(self.calculated_data, symbol, interval, suffix="heikin_ashi")
            logger.info(f"Heikin Ashi df columns: {self.calculated_data.columns.tolist()}")
            logger.info(f"Heikin Ashi df head: \n{self.calculated_data.head().to_string()}")
        except Exception as e:
            logger.error(f"Error calculating Heikin Ashi: {e}")
            self.calculated_data = pd.DataFrame(columns=['open_time', 'ha_open', 'ha_high', 'ha_low', 'ha_close', 'close'])
        return self.calculated_data