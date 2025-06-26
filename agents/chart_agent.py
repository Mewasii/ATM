import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd
from datetime import datetime
from utils.data_processor import calculate_heikin_ashi

class ChartAgent:
    def __init__(self):
        self.output_dir = "data/processed"

    def plot_combined_charts(self, df, symbol="BTCUSDT", save=False):
        ha_df = calculate_heikin_ashi(df)
        """
        Plot standard candlestick and Heikin Ashi charts in subplots.
        Args:
            df (pandas.DataFrame): DataFrame with columns [open_time, open, high, low, close].
            symbol (str): Trading pair symbol.
            save (bool): If True, save the chart as HTML.
        Returns:
            plotly.graph_objects.Figure: The combined chart.
        """
        # Calculate Heikin Ashi data
        ha_df = calculate_heikin_ashi(df)

        # Create subplots
        fig = sp.make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(f"{symbol} Candlestick", f"{symbol} Heikin Ashi"),
            row_heights=[0.5, 0.5]
        )

        # Standard Candlestick
        fig.add_trace(
            go.Candlestick(
                x=df['open_time'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name="Candlestick"
            ),
            row=1, col=1
        )

        # Heikin Ashi Candlestick
        fig.add_trace(
            go.Candlestick(
                x=ha_df['open_time'],
                open=ha_df['ha_open'],
                high=ha_df['ha_high'],
                low=ha_df['ha_low'],
                close=ha_df['ha_close'],
                name="Heikin Ashi",
                increasing_line_color='green',
                decreasing_line_color='red'
            ),
            row=2, col=1
        )

        # Update layout
        fig.update_layout(
            title=f"{symbol} Price Analysis",
            xaxis_title="Time",
            yaxis_title="Price (USDT)",
            xaxis2_title="Time",
            yaxis2_title="Price (USDT)",
            xaxis_rangeslider_visible=False,
            showlegend=True,
            height=800
        )

        # Update x-axes to share zooming
        fig.update_xaxes(matches='x')

        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(f"{self.output_dir}/{symbol}_combined_{timestamp}.html")

        return fig

    def plot_candlestick(self, df, symbol="BTCUSDT", save=False):
        """
        Plot a standard candlestick chart (kept for compatibility).
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
        Plot a line chart of closing prices (kept for compatibility).
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