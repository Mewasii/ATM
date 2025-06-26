from autogen import UserProxyAgent
from agents.binance_agent import BinanceAgent
from agents.chart_agent import ChartAgent

class BinanceUserProxy:
    def __init__(self):
        self.binance_agent = BinanceAgent()
        self.chart_agent = ChartAgent()
        self.user_proxy = UserProxyAgent(
            name="BinanceUserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2
        )

    def run_workflow(self, symbol="BTCUSDT", interval="1h", limit=100, chart_type="candlestick"):
        """
        Run the workflow to fetch data and generate a chart.
        Args:
            symbol (str): Trading pair (e.g., BTCUSDT).
            interval (str): Time interval (e.g., 1h).
            limit (int): Number of data points.
            chart_type (str): Type of chart (candlestick, line, combined).
        """
        # Configure Binance agent
        self.binance_agent.set_symbol(symbol)
        self.binance_agent.set_interval(interval)

        # Fetch data
        data = self.binance_agent.fetch_klines(limit=limit)

        # Generate chart
        if chart_type.lower() == "candlestick":
            fig = self.chart_agent.plot_candlestick(data, symbol, save=True)
        elif chart_type.lower() == "line":
            fig = self.chart_agent.plot_line(data, symbol, save=True)
        elif chart_type.lower() == "combined":
            fig = self.chart_agent.plot_combined_charts(data, symbol, save=True)
        else:
            raise ValueError("Unsupported chart type. Use 'candlestick', 'line', or 'combined'.")

        # Display chart
        fig.show()