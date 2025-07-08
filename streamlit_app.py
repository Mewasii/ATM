import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from agents.chart_agent import ChartAgent
from agents.binance_agent import BinanceAgent
from agents.backtest_agent import BacktestAgent
from datetime import datetime, date

st.set_page_config(page_icon="favicon.ico", layout="wide")  # Wide layout
st.title("Chart Dashboard")
chart_agent = ChartAgent()
binance_agent = BinanceAgent()
data_calc_agent = chart_agent.data_calc_agent  # Access DataCalculationAgent

# Cache data fetching
@st.cache_data
def fetch_klines(symbol, interval, start_date):
    binance_agent.set_symbol(symbol)
    binance_agent.set_interval(interval)
    
    # Calculate number of candles based on start_date and current time
    current_time = datetime.utcnow()
    start_time = datetime.combine(start_date, datetime.min.time())
    time_diff = current_time - start_time
    
    # Convert interval to minutes
    interval_map = {
        "1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440
    }
    interval_minutes = interval_map.get(interval, 60)
    
    # Calculate number of candles
    limit = int(time_diff.total_seconds() / (interval_minutes * 60)) + 1
    st.write(f"Calculated number of candles: {limit} for interval {interval}")
    
    df = binance_agent.fetch_klines(limit=limit)
    # Convert open_time to datetime64[ns] with timezone handling
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', utc=True).dt.tz_localize(None)
    df = df.dropna()  # Drop rows with NaN, but keep all columns
    if df.empty:
        st.warning("Fetched DataFrame is empty after dropna, using minimal structure")
        return pd.DataFrame(columns=['open_time', 'open', 'high', 'low', 'close', 'volume'])
    st.write("Raw Fetched DataFrame:", df.head())  # Debug raw data
    st.write("Row count after dropna:", len(df))
    return df

# Input fields
symbol = st.text_input("Symbol (e.g., BTCUSDT)", "BTCUSDT")
interval = st.selectbox("Interval", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)  # Default to 1h
start_date = st.date_input("Start Date", value=date.today())

# Backtest inputs
initial_cash = st.number_input("Initial Capital", min_value=1000, value=100000)
position_size_pct = st.number_input("Position Size (%)", min_value=0.01, max_value=0.20, value=0.10, step=0.01)

# Button to fetch data and plot
if st.button("Fetch Data and Plot"):
    # Fetch data with error handling
    try:
        df = fetch_klines(symbol, interval, start_date)
        st.write("Fetched DataFrame:", df.head())
        st.write("DataFrame columns:", df.columns.tolist())
        st.write("Data types:", df.dtypes)
        # Precompute Heikin Ashi data
        ha_df = data_calc_agent.calculate_heikin_ashi(df)
        st.write("Precomputed Heikin Ashi Data:", ha_df.head() if ha_df is not None and not ha_df.empty else "None or Empty")
        st.write("Heikin Ashi row count:", len(ha_df) if ha_df is not None else 0)
    except Exception as e:
        st.error(f"Error fetching or calculating data: {e}")
        df = pd.DataFrame(columns=['open_time', 'open', 'high', 'low', 'close', 'volume'])
        ha_df = None

    # Optional backtest
    backtest_results = None
    if st.checkbox("Run Backtest with EMA Crossover"):
        try:
            backtest_agent = BacktestAgent(df)
            results = backtest_agent.run_backtest(strategy="ema_crossover", initial_cash=initial_cash, position_size_pct=position_size_pct)
            st.write("Backtest Results:", {k: v for k, v in results.items() if k != 'equity'})
        except Exception as e:
            st.error(f"Error running backtest: {e}")
            backtest_results = None

    # Select chart type
    chart_type = st.selectbox("Select Chart Type:", ["Normal Candlestick", "Heikin Ashi"], index=0)
    chart_type_value = "normal" if chart_type == "Normal Candlestick" else "heikin_ashi"

    # Generate figures with detailed error handling
    try:
        combined_fig = chart_agent.plot_combined_charts(df, symbol=symbol, indicators=["sma"], strategy="ema_crossover", chart_type=chart_type_value, ha_df=ha_df)
        st.write("Combined Fig Data:", [trace.name for trace in combined_fig.data])
    except Exception as e:
        st.error(f"Error generating charts: {e}")
        combined_fig = go.Figure(data=[go.Scatter(x=[0], y=[0], name="Error")], layout=go.Layout(title="Error in Combined Chart"))

    # Display charts
    st.header("Combined Charts")
    st.plotly_chart(combined_fig, use_container_width=True, config={'scrollZoom': True}, key="combined_chart")

    # Note on stored data
    st.write("Note: Heikin Ashi data is precomputed and stored in DataCalculationAgent.")