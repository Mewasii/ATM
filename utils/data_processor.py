import pandas as pd

def calculate_heikin_ashi(df):
    """
    Calculate Heikin Ashi candles from kline data.
    Args:
        df (pandas.DataFrame): DataFrame with columns [open_time, open, high, low, close].
    Returns:
        pandas.DataFrame: DataFrame with Heikin Ashi columns [open_time, ha_open, ha_high, ha_low, ha_close].
    """
    ha_df = df[['open_time']].copy()
    ha_df['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    
    # Initialize HA Open
    ha_df['ha_open'] = df['open'].copy()
    for i in range(1, len(ha_df)):
        ha_df.iloc[i, ha_df.columns.get_loc('ha_open')] = (ha_df.iloc[i-1]['ha_open'] + ha_df.iloc[i-1]['ha_close']) / 2
    
    # Calculate HA High and Low using ha_df for ha_open/ha_close and df for high/low
    ha_df['ha_high'] = pd.concat([df['high'], ha_df['ha_open'], ha_df['ha_close']], axis=1).max(axis=1)
    ha_df['ha_low'] = pd.concat([df['low'], ha_df['ha_open'], ha_df['ha_close']], axis=1).min(axis=1)
    
    return ha_df[['open_time', 'ha_open', 'ha_high', 'ha_low', 'ha_close']]