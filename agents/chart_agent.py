import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd
from datetime import datetime
from agents.data_calculation_agent import DataCalculationAgent
from agents.strategy_agent import StrategyAgent
from agents.indicator_agent import IndicatorAgent

class ChartAgent:
    def __init__(self):
        self.output_dir = "data/processed"
        self.data_calc_agent = DataCalculationAgent()

    def plot_combined_charts(self, df, symbol="BTCUSDT", indicators=None, strategy=None, chart_type="normal"):
        """
        Plot candlestick and optional Heikin Ashi charts with indicators/strategy.
        Args:
            df: DataFrame with ['open_time', 'open', 'high', 'low', 'close']
            symbol: Asset name
            indicators: List of indicators (e.g., ["sma", "rsi"])
            strategy: Strategy name (e.g., "ema_crossover")
            chart_type: "normal" (candlestick only) or "heikin_ashi" (both with strategy on HA)
        Returns:
            Plotly figure
        """
        ha_df = self.data_calc_agent.calculate_heikin_ashi(df)
        show_rsi = indicators and "rsi" in indicators
        total_rows = 1 if chart_type == "normal" else 2
        if show_rsi:
            total_rows += 1

        # Define subplot titles and row heights
        subplot_titles = (
            f"{symbol} Candlestick",
            "RSI" if show_rsi else None
        ) if chart_type == "normal" else (
            f"{symbol} Candlestick",
            f"{symbol} Heikin Ashi",
            "RSI" if show_rsi else None
        )
        row_heights = [0.6, 0.2] if chart_type == "normal" and show_rsi else [1.0]
        if chart_type == "heikin_ashi":
            row_heights = [0.4, 0.4, 0.2] if show_rsi else [0.5, 0.5]

        # Create subplots
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

        # Heikin Ashi chart (if heikin_ashi selected)
        if chart_type == "heikin_ashi":
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
            calc_df = strategy_agent.ema_crossover_strategy(fast_length=9, slow_length=21, use_ha_df=(chart_type == "heikin_ashi"), ha_df=ha_df)

            # EMA lines
            fig.add_trace(
                go.Scatter(
                    x=calc_df['open_time'],
                    y=calc_df['fast_ema'],
                    name="Fast EMA",
                    line=dict(color='orange')
                ),
                row=1 if chart_type == "normal" else 2, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=calc_df['open_time'],
                    y=calc_df['slow_ema'],
                    name="Slow EMA",
                    line=dict(color='blue')
                ),
                row=1 if chart_type == "normal" else 2, col=1
            )

            # Buy signals
            buy_signals = calc_df[calc_df['position'] == 2]
            fig.add_trace(
                go.Scatter(
                    x=buy_signals['open_time'],
                    y=buy_signals['low' if chart_type == "normal" else 'ha_low'] * 0.995,
                    mode='markers',
                    name='Buy Signal',
                    marker=dict(symbol='triangle-up', color='green', size=10)
                ),
                row=1 if chart_type == "normal" else 2, col=1
            )

            # Sell signals
            sell_signals = calc_df[calc_df['position'] == -2]
            fig.add_trace(
                go.Scatter(
                    x=sell_signals['open_time'],
                    y=sell_signals['high' if chart_type == "normal" else 'ha_high'] * 1.005,
                    mode='markers',
                    name='Sell Signal',
                    marker=dict(symbol='triangle-down', color='red', size=10)
                ),
                row=1 if chart_type == "normal" else 2, col=1
            )

        # Technical indicators
        if indicators:
            indicator_agent = IndicatorAgent(df if chart_type == "normal" else ha_df)

            for ind in indicators:
                if ind == "sma":
                    calc_df = indicator_agent.calculate_sma(length=14)
                    fig.add_trace(
                        go.Scatter(
                            x=calc_df['open_time'],
                            y=calc_df['sma'],
                            name="SMA",
                            line=dict(color='blue')
                        ),
                        row=1 if chart_type == "normal" else 2, col=1
                    )

                elif ind == "rsi" and show_rsi:
                    calc_df = indicator_agent.calculate_rsi(length=14)
                    fig.add_trace(
                        go.Scatter(
                            x=calc_df['open_time'],
                            y=calc_df['rsi'],
                            name="RSI",
                            line=dict(color='purple')
                        ),
                        row=2 if chart_type == "normal" else 3, col=1
                    )

        # Hide unused subplots
        if not show_rsi:
            fig.update_layout(
                yaxis2=dict(visible=False) if chart_type == "normal" else None,
                yaxis3=dict(visible=False) if chart_type == "heikin_ashi" else None,
            )

        fig.update_layout(
            title=f"{symbol} Price Analysis",
            yaxis_title="Price (USDT)",
            showlegend=True,
            height=1400 if show_rsi else (1000 if chart_type == "heikin_ashi" else 800),
            margin=dict(b=50, t=100),
            dragmode=False,
        )

        fig.update_xaxes(rangeslider_visible=False, fixedrange=True)
        fig.update_yaxes(showgrid=True, fixedrange=False, scaleanchor=None)

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
                name="Equity Curve",
                line=dict(color='green')
            )
        )

        fig.update_layout(
            title=f"{symbol} Equity Curve",
            yaxis_title="Portfolio Value (USDT)",
            height=800,
            margin=dict(b=50, t=100),
            dragmode=False,
        )

        fig.update_xaxes(rangeslider_visible=False, fixedrange=True)
        fig.update_yaxes(showgrid=True, fixedrange=False)

        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(f"{self.output_dir}/{symbol}_equity_{timestamp}.html")

        return fig