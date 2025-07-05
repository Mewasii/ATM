import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd
from datetime import datetime
from agents.data_calculation_agent import DataCalculationAgent
from agents.strategy_agent import StrategyAgent
from agents.indicator_agent import IndicatorAgent

class ChartAgent:
    def __init__(self):
        """Initialize ChartAgent with a DataCalculationAgent instance."""
        self.output_dir = "data/processed"
        self.data_calc_agent = DataCalculationAgent()

    def _validate_df(self, df):
        """Validate DataFrame with lenient checks."""
        required_columns = ['open_time', 'open', 'high', 'low', 'close']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        if df.empty:
            raise ValueError("DataFrame is empty")
        if df[required_columns].isnull().any().any():
            print("Warning: DataFrame contains null values, proceeding with available data")

    def plot_combined_charts(self, df, symbol="BTCUSDT", indicators=None, strategy=None, chart_type="normal", save=False, ha_df=None):
        """
        Plot combined charts with range slider for x-axis control, increased spacing, and entry/exit signals.
        Args:
            df: DataFrame with ['open_time', 'open', 'high', 'low', 'close']
            symbol: Trading pair symbol (default: BTCUSDT)
            indicators: List of indicators (e.g., ['sma', 'rsi'])
            strategy: Strategy name (e.g., 'ema_crossover')
            chart_type: 'normal' (candlestick only) or 'heikin_ashi' (both with strategy on HA)
            save: Save chart to HTML file (default: False)
            ha_df: Precomputed Heikin Ashi DataFrame (optional, overrides data_calc_agent)
        Returns:
            Plotly figure object
        """
        self._validate_df(df)
        indicators = indicators or []
        show_rsi = "rsi" in indicators

        # Use precomputed ha_df if provided, else calculate
        ha_df = ha_df if ha_df is not None else (self.data_calc_agent.calculate_heikin_ashi(df) if chart_type == "heikin_ashi" else None)
        print(f"chart_type: {chart_type}, ha_df available: {ha_df is not None}, ha_df columns: {ha_df.columns.tolist() if ha_df is not None else 'None'}")

        total_rows = 1 + (1 if chart_type == "heikin_ashi" else 0) + (1 if show_rsi else 0)
        row_heights = [1.0] * total_rows
        if chart_type == "heikin_ashi" and show_rsi:
            row_heights = [0.4, 0.4, 0.2]
        elif chart_type == "heikin_ashi":
            row_heights = [0.5, 0.5]
        elif show_rsi:
            row_heights = [0.7, 0.3]

        subplot_titles = [f"{symbol} Candlestick"] + ([f"{symbol} Heikin Ashi"] if chart_type == "heikin_ashi" else []) + (["RSI"] if show_rsi else [])

        fig = sp.make_subplots(
            rows=total_rows, cols=1, shared_xaxes=True, vertical_spacing=0.30,
            subplot_titles=subplot_titles, row_heights=row_heights
        )

        # Add Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df['open_time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
                name="Candlestick"
            ),
            row=1, col=1
        )

        # Add Heikin Ashi chart with debug
        if chart_type == "heikin_ashi" and ha_df is not None:
            print("Adding Heikin Ashi trace, ha_df columns:", ha_df.columns.tolist())
            if not ha_df.empty:
                fig.add_trace(
                    go.Candlestick(
                        x=ha_df['open_time'], open=ha_df['ha_open'], high=ha_df['ha_high'],
                        low=ha_df['ha_low'], close=ha_df['ha_close'],
                        name="Heikin Ashi", increasing_line_color='green', decreasing_line_color='red'
                    ),
                    row=2, col=1
                )

        if strategy:
            strategy_agent = StrategyAgent(df)
            calc_df = strategy_agent.ema_crossover_strategy(
                fast_length=9, slow_length=21, use_ha_df=(chart_type == "heikin_ashi"), ha_df=ha_df
            )

            # Add EMA lines
            fig.add_trace(
                go.Scatter(x=calc_df['open_time'], y=calc_df['fast_ema'], name="Fast EMA", line=dict(color='orange')),
                row=1 if chart_type == "normal" else 2, col=1
            )
            fig.add_trace(
                go.Scatter(x=calc_df['open_time'], y=calc_df['slow_ema'], name="Slow EMA", line=dict(color='blue')),
                row=1 if chart_type == "normal" else 2, col=1
            )

            # Add buy signals with labels below
            buy_signals = calc_df[calc_df['position'] == 1]
            for i, row in buy_signals.iterrows():
                entry_id = row['entry_id'] if pd.notna(row['entry_id']) else "N/A"
                fig.add_trace(
                    go.Scatter(
                        x=[row['open_time']], y=[row['low'] * 0.995 if chart_type == "normal" else row['ha_low'] * 0.995],
                        mode='markers', name=f'Buy {entry_id}', marker=dict(symbol='triangle-up', color='green', size=10)
                    ),
                    row=1 if chart_type == "normal" else 2, col=1
                )
                fig.add_annotation(
                    x=row['open_time'], y=row['low'] * 0.99 if chart_type == "normal" else row['ha_low'] * 0.99,
                    text=entry_id, showarrow=False, yshift=-10, font=dict(size=10),
                    row=1 if chart_type == "normal" else 2, col=1
                )

            # Add sell signals with labels above
            sell_signals = calc_df[calc_df['position'] == -1]
            for i, row in sell_signals.iterrows():
                entry_id = row['entry_id'] if pd.notna(row['entry_id']) else "N/A"
                fig.add_trace(
                    go.Scatter(
                        x=[row['open_time']], y=[row['high'] * 1.005 if chart_type == "normal" else row['ha_high'] * 1.005],
                        mode='markers', name=f'Sell {entry_id}', marker=dict(symbol='triangle-down', color='red', size=10)
                    ),
                    row=1 if chart_type == "normal" else 2, col=1
                )
                fig.add_annotation(
                    x=row['open_time'], y=row['high'] * 1.01 if chart_type == "normal" else row['ha_high'] * 1.01,
                    text=entry_id, showarrow=False, yshift=10, font=dict(size=10),
                    row=1 if chart_type == "normal" else 2, col=1
                )

        if indicators:
            indicator_agent = IndicatorAgent(df if chart_type == "normal" else ha_df)
            for ind in indicators:
                if ind == "sma":
                    calc_df = indicator_agent.calculate_sma(length=14)
                    fig.add_trace(
                        go.Scatter(x=calc_df['open_time'], y=calc_df['sma'], name="SMA", line=dict(color='blue')),
                        row=1 if chart_type == "normal" else 2, col=1
                    )
                elif ind == "rsi" and show_rsi:
                    calc_df = indicator_agent.calculate_rsi(length=14)
                    fig.add_trace(
                        go.Scatter(x=calc_df['open_time'], y=calc_df['rsi'], name="RSI", line=dict(color='purple')),
                        row=total_rows, col=1
                    )

        fig.update_layout(
            title=f"{symbol} Price Analysis",
            yaxis_title="Price (USDT)",
            showlegend=True,
            height=1400 if total_rows > 1 else 800,
            margin=dict(b=50, t=100),
            dragmode='zoom',
            xaxis=dict(rangeslider=dict(visible=True), rangeselector=dict(visible=True))
        )
        fig.update_xaxes(rangeslider_visible=True, fixedrange=False)
        fig.update_yaxes(showgrid=True, fixedrange=False, scaleanchor=None)

        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(f"{self.output_dir}/{symbol}_combined_{timestamp}.html")

        return fig

    def plot_candlestick(self, df, symbol="BTCUSDT", save=False):
        """Plot a standalone candlestick chart."""
        self._validate_df(df)
        fig = go.Figure(data=[go.Candlestick(
            x=df['open_time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name=symbol
        )])
        fig.update_layout(
            title=f"{symbol} Candlestick Chart", yaxis_title="Price (USDT)", height=800, margin=dict(b=50, t=100),
            dragmode='zoom', xaxis=dict(rangeslider=dict(visible=True), rangeselector=dict(visible=True))
        )
        fig.update_xaxes(rangeslider_visible=True, fixedrange=False)
        fig.update_yaxes(showgrid=True)
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(f"{self.output_dir}/{symbol}_candlestick_{timestamp}.html")
        return fig

    def plot_line(self, df, symbol="BTCUSDT", save=False):
        """Plot a standalone line chart of closing prices."""
        self._validate_df(df)
        fig = go.Figure(data=[go.Scatter(x=df['open_time'], y=df['close'], mode='lines', name=symbol)])
        fig.update_layout(
            title=f"{symbol} Closing Price", yaxis_title="Price (USDT)", height=800, margin=dict(b=50, t=100),
            dragmode='zoom', xaxis=dict(rangeslider=dict(visible=True), rangeselector=dict(visible=True))
        )
        fig.update_xaxes(rangeslider_visible=True, fixedrange=False)
        fig.update_yaxes(showgrid=True)
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(f"{self.output_dir}/{symbol}_line_{timestamp}.html")
        return fig

    def plot_equity_curve(self, df, backtest_results, symbol="BTCUSDT", save=False):
        """Plot the equity curve from backtest results."""
        self._validate_df(df)
        if not backtest_results or len(backtest_results) != len(df):
            backtest_results = [0] * len(df)
        fig = go.Figure(data=[go.Scatter(x=df['open_time'], y=backtest_results, mode='lines', name="Equity Curve", line=dict(color='green'))])
        fig.update_layout(
            title=f"{symbol} Equity Curve", yaxis_title="Portfolio Value (USDT)", height=800, margin=dict(b=50, t=100),
            dragmode='zoom', xaxis=dict(rangeslider=dict(visible=True), rangeselector=dict(visible=True))
        )
        fig.update_xaxes(rangeslider_visible=True, fixedrange=False)
        fig.update_yaxes(showgrid=True, fixedrange=False)
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig.write_html(f"{self.output_dir}/{symbol}_equity_{timestamp}.html")
        return fig