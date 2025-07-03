import pandas as pd
import backtrader as bt
from strategies.strategy_registry import StrategyRegistry

class BacktestAgent:
    def __init__(self, df=None):
        """
        Initialize BacktestAgent with an optional DataFrame.
        Args:
            df: DataFrame with price data (default None)
        """
        self.df = df.copy() if df is not None else None

    def run_backtest(self, strategy="ema_crossover", initial_cash=100000, commission=0.001):
        """
        Run a backtest using the specified strategy.
        Args:
            strategy: Name of the strategy to backtest (default: "ema_crossover")
            initial_cash: Initial capital for the backtest (default: 100000)
            commission: Trading commission per trade (default: 0.001)
        Returns:
            Dictionary with backtest results (initial_cash, final_value, profit, profit_pct, equity)
        """
        if self.df is None or self.df.empty:
            raise ValueError("DataFrame is not set or empty. Please provide a valid DataFrame.")

        # Validate required columns
        required_columns = ['open_time', 'open', 'high', 'low', 'close']
        if not all(col in self.df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")

        # Create a backtrader data feed
        try:
            data = bt.feeds.PandasData(dataname=self.df, datetime='open_time')
        except Exception as e:
            raise ValueError(f"Error creating backtrader data feed: {e}")

        # Initialize Cerebro engine
        cerebro = bt.Cerebro()

        # Get strategy class from registry
        try:
            strategy_class = StrategyRegistry.get_strategy(strategy)
        except Exception as e:
            raise ValueError(f"Error loading strategy '{strategy}': {e}")

        cerebro.addstrategy(strategy_class)

        # Add data feed and configure broker
        cerebro.adddata(data)
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=commission)

        # Run backtest
        try:
            strats = cerebro.run()
            strategy_instance = strats[0]
        except Exception as e:
            raise RuntimeError(f"Error running backtest: {e}")

        # Extract results
        final_value = cerebro.broker.getvalue()
        profit = final_value - initial_cash
        return {
            'initial_cash': initial_cash,
            'final_value': final_value,
            'profit': profit,
            'profit_pct': (profit / initial_cash) * 100,
            'equity': strategy_instance.equity
        }