import streamlit as st
import pandas as pd
import numpy as np
from agents.chart_agent import ChartAgent
from agents.binance_agent import BinanceAgent
from agents.backtest_agent import BacktestAgent

st.set_page_config(page_icon="favicon.ico", layout="wide")  # Wide layout
st.title("Chart Dashboard")
chart_agent = ChartAgent()
binance_agent = BinanceAgent()
backtest_agent = BacktestAgent(None)  # Initialize without df, will pass later

# Fetch real data with user-adjustable parameters
symbol = st.text_input("Symbol (e.g., BTCUSDT)", "BTCUSDT")
interval = st.selectbox("Interval", ["1m", "5m", "15m", "1h", "1d"], index=3)  # Default to 1h
limit = st.number_input("Limit (number of candles)", min_value=10, value=100)
binance_agent.set_symbol(symbol)
binance_agent.set_interval(interval)
df = binance_agent.fetch_klines(limit=limit)
st.write("Fetched df:", df.head())  # Debug

# Optional backtest
backtest_results = None
if st.checkbox("Run Backtest with EMA Crossover"):
    backtest_agent.df = df  # Set df for backtest
    results = backtest_agent.run_backtest(strategy="ema_crossover")
    st.write("Backtest Results:", {k: v for k, v in results.items() if k != 'equity'})
    backtest_results = results.get('equity', [0])  # Fallback to [0] if None

# Toggle button
chart_type = st.selectbox("Select Chart Type:", ["Normal Candlestick", "Heikin Ashi"], index=0)
chart_type_value = "normal" if chart_type == "Normal Candlestick" else "heikin_ashi"

# Generate figures with debug print
equity_fig = chart_agent.plot_equity_curve(df, backtest_results if backtest_results else [0])  # Fallback to [0]
combined_fig = chart_agent.plot_combined_charts(df, indicators=["sma"], strategy="ema_crossover", chart_type=chart_type_value)
print("Combined Fig Data:", combined_fig.data)  # Debug to check traces

# Display charts
st.header("Equity Curve")
st.plotly_chart(equity_fig, use_container_width=True, config={'scrollZoom': True})

st.header("Combined Charts")
st.plotly_chart(combined_fig, use_container_width=True, config={'scrollZoom': True})

# Display stored data
st.write("Stored Heikin Ashi data:", chart_agent.data_calc_agent.calculated_data)
st.write("Stored Original data:", chart_agent.data_calc_agent.original_data)