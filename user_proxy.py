from autogen import UserProxyAgent
from agents.binance_agent import BinanceAgent
from agents.chart_agent import ChartAgent
from agents.backtest_agent import BacktestAgent  # <-- THÊM DÒNG NÀY

class BinanceUserProxy:
    def __init__(self):
        self.binance_agent = BinanceAgent()
        self.chart_agent = ChartAgent()
        self.user_proxy = UserProxyAgent(
            name="BinanceUserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2
        )

    def run_workflow(self, symbol, interval, limit, chart_type, indicators=None, strategy=None):
        """
        Run the workflow: fetch data, generate chart, and optionally run backtest.

        Args:
            symbol (str): Trading pair (e.g., BTCUSDT).
            interval (str): Time interval (e.g., 1h).
            limit (int): Number of candles to fetch.
            chart_type (str): Chart type ("candlestick", "line", or "combined").
            indicators (list): List of indicators (e.g., ["sma", "rsi"]).
            strategy (str): Strategy name to backtest (e.g., "ema_crossover").
        """

        # Lấy dữ liệu từ Binance
        self.binance_agent.set_symbol(symbol)
        self.binance_agent.set_interval(interval)
        df = self.binance_agent.fetch_klines(limit=limit)

        # Vẽ biểu đồ
        if chart_type.lower() == "candlestick":
            fig = self.chart_agent.plot_candlestick(df, symbol, save=True)
        elif chart_type.lower() == "line":
            fig = self.chart_agent.plot_line(df, symbol, save=True)
        elif chart_type.lower() == "combined":
            fig = self.chart_agent.plot_combined_charts(df, symbol=symbol, indicators=indicators, strategy=strategy, save=True)
        else:
            raise ValueError("Unsupported chart type. Use 'candlestick', 'line', or 'combined'.")

        fig.show()

        # Chạy backtest nếu có chiến lược
        if strategy:
            print(f"\n🔍 Running backtest for strategy: {strategy}")
            backtest_agent = BacktestAgent(df)
            results = backtest_agent.run_backtest(strategy=strategy)
            print("📊 Backtest Results:")
            for key, value in results.items():
                if key != 'equity':  # Không in danh sách equity dài
                   print(f"{key}: {value}")

            # Vẽ equity curve
            equity_curve = results.get('equity', [])
            if equity_curve:
                fig_equity = self.chart_agent.plot_equity_curve(df, equity_curve, symbol, save=True)
                fig_equity.show()