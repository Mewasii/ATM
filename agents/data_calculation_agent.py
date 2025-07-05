import pandas as pd

class DataCalculationAgent:
    def __init__(self):
        """Initialize DataCalculationAgent with storage for original and calculated data."""
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
        print("Calculating Heikin Ashi with df columns:", df.columns.tolist())
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
            self.calculated_data = ha_df[['open_time', 'ha_open', 'ha_high', 'ha_low', 'ha_close', 'close']].fillna(0)  # Avoid dropping all rows
            if self.calculated_data.empty:
                print("Warning: Heikin Ashi data is empty after processing")
                self.calculated_data = ha_df[['open_time', 'ha_open', 'ha_high', 'ha_low', 'ha_close', 'close']].fillna(0)
            # Debug comparison
            print("Sample comparison - Original vs Heikin Ashi:")
            print(df[['open_time', 'open', 'high', 'low', 'close']].head().to_string())
            print(self.calculated_data[['open_time', 'ha_open', 'ha_high', 'ha_low', 'ha_close']].head().to_string())
        except Exception as e:
            print(f"Error calculating Heikin Ashi: {e}")
            self.calculated_data = pd.DataFrame(columns=['open_time', 'ha_open', 'ha_high', 'ha_low', 'ha_close', 'close'])
        print("Heikin Ashi df columns:", self.calculated_data.columns.tolist())
        print("Heikin Ashi df head:", self.calculated_data.head().to_string())
        return self.calculated_data