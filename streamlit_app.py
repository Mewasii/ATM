import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from agents.chart_agent import ChartAgent
from agents.historical_data_agent import HistoricalDataAgent
from agents.backtest_agent import BacktestAgent
from datetime import datetime, date
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(page_icon="favicon.ico", layout="wide")
st.title("Real-Time Chart Dashboard")

# Initialize agents
chart_agent = ChartAgent()
historical_agent = HistoricalDataAgent()

# Initialize session state
if 'data_file' not in st.session_state:
    st.session_state.data_file = None
if 'websocket_running' not in st.session_state:
    st.session_state.websocket_running = False

# Input fields
with st.sidebar:
    st.header("Settings")
    symbol = st.text_input("Symbol (e.g., BTCUSDT)", "BTCUSDT")
    interval = st.selectbox("Interval", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)
    start_date = st.date_input("Start Date", value=date(2019, 1, 1))
    chart_type = st.selectbox("Chart Type", ["Normal Candlestick", "Heikin Ashi"], index=0)
    chart_type_value = "normal" if chart_type == "Normal Candlestick" else "heikin_ashi"
    initial_cash = st.number_input("Initial Capital", min_value=1000, value=100000)
    position_size_pct = st.number_input("Position Size (%)", min_value=0.01, max_value=0.20, value=0.10, step=0.01)
    enable_websocket = st.checkbox("Enable Real-Time Updates (WebSocket)", value=False)
    run_backtest = st.checkbox("Run Backtest with EMA Crossover", value=False)

# Set data file path
data_file = os.path.join("data/raw", f"{symbol}_{interval}.csv")
st.session_state.data_file = data_file

# Fetch initial data
if st.button("Fetch Historical Data"):
    try:
        historical_agent.set_symbol(symbol)
        historical_agent.set_interval(interval)
        if not os.path.exists(data_file):
            logger.info(f"Fetching historical data for {symbol} at {interval} from {start_date}")
            historical_agent.collect_historical_data(start_date=start_date.strftime("%Y-%m-%d"))
        df = historical_agent.read_data()
        if df.empty:
            st.warning("No data available for the selected symbol and interval")
        else:
            st.write("Loaded DataFrame:", df.head())
        # Precompute Heikin Ashi
        chart_agent.data_calc_agent.calculate_heikin_ashi(data_file, symbol, interval)
    except Exception as e:
        st.error(f"Error fetching or calculating data: {e}")

# Handle WebSocket
if enable_websocket and not st.session_state.websocket_running:
    try:
        historical_agent.set_symbol(symbol)
        historical_agent.set_interval(interval)
        historical_agent.start_websocket()
        st.session_state.websocket_running = True
        st.write("Started WebSocket for real-time updates.")
    except Exception as e:
        st.error(f"Error starting WebSocket: {e}")

if not enable_websocket and st.session_state.websocket_running:
    try:
        historical_agent.stop_websocket()
        st.session_state.websocket_running = False
        st.write("Stopped WebSocket.")
    except Exception as e:
        st.error(f"Error stopping WebSocket: {e}")

# Run backtest if enabled
backtest_results = None
if run_backtest and os.path.exists(data_file):
    try:
        backtest_agent = BacktestAgent(data_file)
        results = backtest_agent.run_backtest(
            strategy="ema_crossover",
            initial_cash=initial_cash,
            position_size_pct=position_size_pct,
            symbol=symbol,
            interval=interval
        )
        backtest_results = results.get('equity', [])
        st.write("Backtest Results:", {k: v for k, v in results.items() if k != 'equity'})
    except Exception as e:
        st.error(f"Error running backtest: {e}")

# Plot charts
if os.path.exists(data_file):
    try:
        combined_fig = chart_agent.plot_combined_charts(
            data_file,
            symbol=symbol,
            interval=interval,
            indicators=["sma", "rsi"],
            strategy="ema_crossover",
            chart_type=chart_type_value
        )
        st.header("Real-Time Combined Charts")
        st.plotly_chart(combined_fig, use_container_width=True, config={'scrollZoom': True}, key="combined_chart")
        
        # Plot equity curve if backtest was run
        if backtest_results:
            equity_fig = chart_agent.plot_equity_curve(data_file, symbol=symbol, interval=interval)
            st.header("Equity Curve")
            st.plotly_chart(equity_fig, use_container_width=True, config={'scrollZoom': True}, key="equity_chart")
    except Exception as e:
        st.error(f"Error generating charts: {e}")

# Auto-refresh for real-time updates
if st.session_state.websocket_running:
    st.experimental_rerun()

st.write("Note: Real-time updates are enabled when WebSocket is active. Disable to stop auto-refresh.")