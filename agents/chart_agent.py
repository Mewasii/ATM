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

    def calculate_heikin_ashi(self, df):
        """
        Calculate Heikin Ashi candles from OHLC data.
        Args:
            df: DataFrame with columns ['open', 'high', 'low', 'close', 'open_time']
        Returns:
            DataFrame with Heikin Ashi columns ['ha_open', 'ha_high', 'ha_low', 'ha_close', 'open_time']
        """
        # Validate input DataFrame
        required_columns = ['open', 'high', 'low', 'close', 'open_time']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Input DataFrame must contain columns: {required_columns}")

        # Create a copy of the DataFrame
        ha_df = df.copy()

        # Calculate Heikin Ashi columns
        ha_df['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
        ha_df['ha_open'] = (df['open'].shift(1) + df['close'].shift(1)) / 2
        ha_df['ha_open'].iloc[0] = (df['open'].iloc[0] + df['close'].iloc[0]) / 2

        # Use ha_df for ha_high and ha_low to reference ha_open and ha_close
        ha_df['ha_high'] = ha_df[['high', 'ha_open', 'ha_close']].max(axis=1)
        ha_df['ha_low'] = ha_df[['low', 'ha_open', 'ha_close']].min(axis=1)

        return ha_df

    def plot_combined_charts(self, df, symbol="BTCUSDT", indicators=None, strategy=None, chart_type="normal", save=False):
        """
        Plot combined charts (Candlestick, Heikin Ashi, indicators).
        Args:
            df: DataFrame with price data
            symbol: Trading pair symbol (default: BTCUSDT)
            indicators: List of indicators to plot (e.g., ['sma', 'rsi'])
            strategy: Trading strategy to apply (e.g., 'ema_crossover')
            chart_type: Chart type ('normal' or 'heikin_ashi')
            save: Save chart to HTML file (default: False)
        Returns:
            Plotly figure object
        """
        indicators = indicators or []
        show_rsi = "rsi" in indicators
        ha_df = self.calculate_heikin_ashi(df) if chart_type == "heikin_ashi" else None

        total_rows = 1
        if chart_type == "heikin_ashi":
            total_rows += 1
        if show_rsi:
            total_rows += 1

        row_heights = [0.6]
        if chart_type == "heikin_ashi" and show_rsi:
            row_heights = [0.4, 0.3, 0.2]
        elif chart_type == "heikin_ashi":
            row_heights = [0.5, 0.5]
        elif show_rsi:
            row_heights = [0.7, 0.3]

        subplot_titles = [f"{symbol} Candlestick"]
        if chart_type == "heikin_ashi":
            subplot_titles.append(f"{symbol} Heikin Ashi")
        if show_rsi:
            subplot_titles.append("RSI")

        fig = sp.make_subplots(
            rows=total_rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=subplot_titles,
            row_heights=row_heights
        )

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

        if chart_type == "heikin_ashi" and ha_df is not None:
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

        if strategy:
            strategy_agent = StrategyAgent(df)
            df = strategy_agent.apply_strategy(strategy, fast_length=9, slow_length=21)

            if strategy.lower() == "ema_crossover":
                fig.add_trace(
                    go.Scatter(
                        x=df['open_time'],
                        y=df['fast_ema'],
                        name="Fast EMA",
                        line=dict(color='orange')
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=df['open_time'],
                        y=df['slow_ema'],
                        name="Slow EMA",
                        line=dict(color='blue')
                    ),
                    row=1, col=1
                )
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

        if indicators:
            indicator_agent = IndicatorAgent(df)
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
                        row=total_rows, col=1
                    )

        fig.update_layout(
            title=f"{symbol} Price Analysis",
            yaxis_title="Price (USDT)",
            showlegend=True,
            height=1000 if total_rows > 1 else 800,
            margin=dict(b=50, t=100),
            dragmode=False
        )

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
            margin=dict(b=50, t=100)
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
            margin=dict(b=50, t=100)
        )

        fig.update_yaxes(showgrid=True)
        fig.update_xaxes(rangeslider_visible=False)

        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(f"{self.output_dir}/{symbol}_line_{timestamp}.html")

        return fig

    def plot_equity_curve(self, df, backtest_results, symbol="BTCUSDT", save=False):
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
            dragmode=False
        )

        fig.update_xaxes(rangeslider_visible=False, fixedrange=True)
        fig.update_yaxes(showgrid=True, fixedrange=False)

        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(f"{self.output_dir}/{symbol}_equity_{timestamp}.html")

        return fig