import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd
from datetime import datetime

from utils.data_processor import calculate_heikin_ashi
from agents.indicator_agent import IndicatorAgent
from agents.strategy_agent import StrategyAgent

class ChartAgent:
    def __init__(self):
        self.output_dir = "data/processed"

    def plot_combined_charts(self, df, symbol="BTCUSDT", indicators=None, strategy=None, save=False):
        """
        Plot standard candlestick and Heikin Ashi charts in subplots, with optional RSI subplot.
        Uses Plotly's default interactions, with no custom interaction logic.
        """
        ha_df = calculate_heikin_ashi(df)
        show_rsi = indicators and "rsi" in indicators
        total_rows = 3 if show_rsi else 2

        # Define subplot titles and row heights based on show_rsi
        subplot_titles = (
            f"{symbol} Candlestick",
            f"{symbol} Heikin Ashi",
            "RSI"
        ) if show_rsi else (
            f"{symbol} Candlestick",
            f"{symbol} Heikin Ashi"
        )
        
        row_heights = [0.4, 0.4, 0.2] if show_rsi else [0.5, 0.5]

        # Create subplots with the correct number of rows
        fig = sp.make_subplots(
            rows=total_rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=subplot_titles,
            row_heights=row_heights
        )

        # Candlestick chart
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

        # Heikin Ashi chart
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

        # Strategy
        if strategy:
            strategy_agent = StrategyAgent(df)

            if strategy.lower() == "ema_crossover":
                df = strategy_agent.ema_crossover_strategy(fast_length=9, slow_length=21)

                # Fast EMA
                fig.add_trace(
                    go.Scatter(
                        x=df['open_time'],
                        y=df['fast_ema'],
                        name="Fast EMA",
                        line=dict(color='orange')
                    ),
                    row=1, col=1
                )

                # Slow EMA
                fig.add_trace(
                    go.Scatter(
                        x=df['open_time'],
                        y=df['slow_ema'],
                        name="Slow EMA",
                        line=dict(color='blue')
                    ),
                    row=1, col=1
                )

                # Buy signals
                buy_signals = df[df['position'] == 2]
                fig.add_trace(
                    go.Scatter(
                        x=buy_signals['open_time'],
                        y=buy_signals['low'] * 0.995,
                        mode='markers',
                        name='Buy Signal',
                        marker=dict(symbol='triangle-up', color='green', size=10)
                    ),
                    row=1, col=1
                )

                # Sell signals
                sell_signals = df[df['position'] == -2]
                fig.add_trace(
                    go.Scatter(
                        x=sell_signals['open_time'],
                        y=sell_signals['high'] * 1.005,
                        mode='markers',
                        name='Sell Signal',
                        marker=dict(symbol='triangle-down', color='red', size=10)
                    ),
                    row=1, col=1
                )

        # Technical indicators
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

                elif ind == "rsi" and show_rsi:
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

        # Hide any residual third subplot when RSI is not shown
        if not show_rsi:
            fig.update_layout(
                yaxis3=dict(visible=False),
            )

        fig.update_layout(
            title=f"{symbol} Price Analysis",
            yaxis_title="Price (USDT)",
            showlegend=True,
            height=1400 if show_rsi else 1000,
            margin=dict(b=50, t=100),
        )

        # Ensure grids are visible on all subplots and disable rangeslider
        fig.update_yaxes(showgrid=True)
        fig.update_xaxes(rangeslider_visible=False)

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
            height=800,
            margin=dict(b=50, t=100),
        )

        fig.update_yaxes(showgrid=True)
        fig.update_xaxes(rangeslider_visible=False)

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
        )

        fig.update_yaxes(showgrid=True)
        fig.update_xaxes(rangeslider_visible=False)

        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(f"{self.output_dir}/{symbol}_line_{timestamp}.html")

        return fig

    def plot_equity_curve(self, df, backtest_results, symbol="BTCUSDT", save=False):
        """
        Plot the equity curve from backtest results.
        """
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df['open_time'],
                y=backtest_results,
                mode='lines',
                name='Equity Curve',
                line=dict(color='green')
            )
        )

        fig.update_layout(
            title=f"{symbol} Equity Curve",
            yaxis_title="Portfolio Value (USDT)",
            height=800,
            margin=dict(b=50, t=100),
        )

        fig.update_yaxes(showgrid=True)
        fig.update_xaxes(rangeslider_visible=False)

        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(f"{self.output_dir}/{symbol}_equity_{timestamp}.html")

        return fig