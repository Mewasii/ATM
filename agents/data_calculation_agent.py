from utils.data_processor import calculate_heikin_ashi
import pandas as pd

class DataCalculationAgent:
    def __init__(self):
        self.original_data = None
        self.calculated_data = None

    def calculate_heikin_ashi(self, df):
        """
        Calculate Heikin Ashi data and store both original and calculated data.
        Args:
            df: DataFrame with columns ['open_time', 'open', 'high', 'low', 'close']
        Returns:
            DataFrame with Heikin Ashi data
        """
        self.original_data = df.copy()
        self.calculated_data = calculate_heikin_ashi(df)
        if self.calculated_data is None or self.calculated_data.empty:
            print("Warning: Heikin Ashi calculation failed or returned empty data")
        else:
            print("Heikin Ashi data stored in calculated_data:\n", self.calculated_data.head())
        return self.calculated_data