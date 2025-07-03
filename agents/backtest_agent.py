import pandas as pd

class BacktestAgent:
    def __init__(self, df=None):
        """
        Initialize BacktestAgent with an optional DataFrame.
        Args:
            df: DataFrame with price data (default None)
        """
        self.df = df.copy() if df is not None else None

    def run_backtest(self, strategy="ema_crossover"):
        """
        Run backtest with the given strategy.
        Args:
            strategy: Strategy name (e.g., "ema_crossover")
        Returns:
            dict: Backtest results including equity curve
        """
        if self.df is None:
            raise ValueError("No data provided for backtest. Set df before running backtest.")
        
        # Example backtest (replace with your logic)
        results = {"equity": [1000 + i * 10 for i in range(len(self.df))], "return": 10.5, "drawdown": 2.3}
        return results