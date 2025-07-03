from autogen import UserProxyAgent
from agents.binance_agent import BinanceAgent
from agents.chart_agent import ChartAgent
from agents.backtest_agent import BacktestAgent

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
        Returns:
            df: DataFrame with price data
            backtest_results: List of equity values (if strategy is provided)
        Args:
            symbol (str): Trading pair (e.g., BTCUSDT).
            interval (str): Time interval (e.g., 1h).
            limit (int): Number of candles to fetch.
            chart_type (str): Chart type ("candlestick", "line", or "combined").
            indicators (list): List of indicators (e.g., ["sma", "rsi"]).
            strategy (str): Strategy name to backtest (e.g., "ema_crossover").
        """
        # Fetch data from Binance
        self.binance_agent.set_symbol(symbol)
        self.binance_agent.set_interval(interval)
        df = self.binance_agent.fetch_klines(limit=limit)

        # Optional backtest
        backtest_results = None
        if strategy:
            print(f"\n🔍 Running backtest for strategy: {strategy}")
            backtest_agent = BacktestAgent(df)
            results = backtest_agent.run_backtest(strategy=strategy)
            print("📊 Backtest Results:")
            for key, value in results.items():
                if key != 'equity':  # Avoid printing long equity list
                    print(f"{key}: {value}")
            backtest_results = results.get('equity', [])

        return df, backtest_results
    
    