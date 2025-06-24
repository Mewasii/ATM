import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

class ChartAgent:
    def __init__(self):
        self.output_dir = "data/processed"

    def plot_candlestick(self, df, symbol="BTCUSDT", save=False):
        """
        Plot a candlestick chart from kline data.
        Args:
            df (pandas.DataFrame): DataFrame with columns [open_time, open, high, low, close].
            symbol (str): Trading pair symbol.
            save (bool): If True, save the chart as HTML.
        Returns:
            plotly.graph_objects.Figure: The generated chart.
        """
        fig = go.Figure(data=[go.Candlestick(
            x=df['open_time'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol
        )])

        fig.update_layout(
            title=f"{symbol} Candlestick Chart",
            xaxis_title="Time",
            yaxis_title="Price (USDT)",
            xaxis_rangeslider_visible=False
        )

        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(f"{self.output_dir}/{symbol}_candlestick_{timestamp}.html")

        return fig

    def plot_line(self, df, symbol="BTCUSDT", save=False):
        """
        Plot a line chart of closing prices.
        Args:
            df (pandas.DataFrame): DataFrame with columns [open_time, close].
            symbol (str): Trading pair symbol.
            save (bool): If True, save the chart as HTML.
        Returns:
            plotly.graph_objects.Figure: The generated chart.
        """
        fig = go.Figure(data=[go.Scatter(
            x=df['open_time'],
            y=df['close'],
            mode='lines',
            name=symbol
        )])

        fig.update_layout(
            title=f"{symbol} Closing Price",
            xaxis_title="Time",
            yaxis_title="Price (USDT)"
        )

        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(f"{self.output_dir}/{symbol}_line_{timestamp}.html")

        return fig