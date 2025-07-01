import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd
from datetime import datetime
from utils.data_processor import calculate_heikin_ashi
from agents.indicator_agent import IndicatorAgent  # Đảm bảo bạn có file này

class ChartAgent:
    def __init__(self):
        self.output_dir = "data/processed"

    def plot_combined_charts(self, df, symbol="BTCUSDT", indicators=None, save=False):
        """
        Plot standard candlestick and Heikin Ashi charts in subplots.
        Args:
            df (pandas.DataFrame): DataFrame with columns [open_time, open, high, low, close].
            symbol (str): Trading pair symbol.
            indicators (list): List of indicators to calculate (e.g., ["sma", "rsi"]).
            save (bool): If True, save the chart as HTML.
        Returns:
            plotly.graph_objects.Figure: The combined chart.
        """

        # Tính Heikin Ashi
        ha_df = calculate_heikin_ashi(df)

        # Kiểm tra xem có vẽ RSI hay không để xác định số subplot
        show_rsi = indicators and "rsi" in indicators
        total_rows = 3 if show_rsi else 2

        # Tạo subplots
        fig = sp.make_subplots(
            rows=total_rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(
                f"{symbol} Candlestick",
                f"{symbol} Heikin Ashi",
                "RSI" if show_rsi else None
            ),
            row_heights=[0.4, 0.4, 0.2] if show_rsi else [0.5, 0.5]
        )

        # Candlestick
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

        # Heikin Ashi
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

        # Chỉ báo kỹ thuật
        if indicators:
            indicator_agent = IndicatorAgent(df)

            for ind in indicators:
                if ind == "sma":
                    df = indicator_agent.calculate_sma(length=14)
                    fig.add_trace(
                        go.Scatter(
                            x=df['open_time'],
                            y=df['sma'],
                            name="SMA",
                            line=dict(color='blue')
                        ),
                        row=1, col=1
                    )

                elif ind == "rsi":
                    df = indicator_agent.calculate_rsi(length=14)
                    fig.add_trace(
                        go.Scatter(
                            x=df['open_time'],
                            y=df['rsi'],
                            name="RSI",
                            line=dict(color='purple')
                        ),
                        row=3, col=1
                    )

        # Layout
        fig.update_layout(
            title=f"{symbol} Price Analysis",
            yaxis_title="Price (USDT)",
            xaxis_rangeslider_visible=False,
            showlegend=True,
            height=1400 if show_rsi else 1000,
            margin=dict(b=50, t=100),
            hovermode='x unified'
        )

        fig.update_xaxes(matches='x')
        fig.update_yaxes(fixedrange=False)

        # Save nếu cần
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(f"{self.output_dir}/{symbol}_combined_{timestamp}.html")

        return fig

    def plot_candlestick(self, df, symbol="BTCUSDT", save=False):
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
            yaxis_title="Price (USDT)",
            xaxis_rangeslider_visible=False,
            height=800,
            margin=dict(b=50, t=100),
            hovermode='x unified'
        )

        fig.update_yaxes(fixedrange=False)

        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(f"{self.output_dir}/{symbol}_candlestick_{timestamp}.html")

        return fig

    def plot_line(self, df, symbol="BTCUSDT", save=False):
        fig = go.Figure(data=[go.Scatter(
            x=df['open_time'],
            y=df['close'],
            mode='lines',
            name=symbol
        )])

        fig.update_layout(
            title=f"{symbol} Closing Price",
            yaxis_title="Price (USDT)",
            height=800,
            margin=dict(b=50, t=100),
            hovermode='x unified'
        )

        fig.update_yaxes(fixedrange=False)

        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(f"{self.output_dir}/{symbol}_line_{timestamp}.html")

        return fig
