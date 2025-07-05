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
        self.initial_capital = 100000  # Default initial capital
        self.total_assets = self.initial_capital
        self.position_size_pct = 0.10  # Default 10% of capital per position

    def run_backtest(self, strategy="ema_crossover", initial_cash=None, commission=0.001, position_size_pct=None):
        """
        Run a backtest using the specified strategy with capital and position sizing.
        Args:
            strategy: Name of the strategy to backtest (default: "ema_crossover")
            initial_cash: Initial capital for the backtest (optional, overrides default)
            commission: Trading commission per trade (default: 0.001)
            position_size_pct: Percentage of capital per position (optional, overrides default)
        Returns:
            Dictionary with backtest results (initial_cash, total_assets, profit, profit_pct, equity)
        """
        if self.df is None or self.df.empty:
            raise ValueError("DataFrame is not set or empty. Please provide a valid DataFrame.")

        # Validate and set parameters
        self.initial_capital = initial_cash if initial_cash is not None else self.initial_capital
        self.total_assets = self.initial_capital
        self.position_size_pct = position_size_pct if position_size_pct is not None else self.position_size_pct
        if not 0 < self.position_size_pct <= 1:
            raise ValueError("Position size percentage must be between 0 and 1.")

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
        cerebro.broker.setcash(self.initial_capital)
        cerebro.broker.setcommission(commission=commission)

        # Run backtest
        try:
            strats = cerebro.run()
            strategy_instance = strats[0]
        except Exception as e:
            raise RuntimeError(f"Error running backtest: {e}")

        # Extract results and update total assets
        final_value = cerebro.broker.getvalue()
        profit = final_value - self.initial_capital
        self.total_assets += profit  # Update total assets
        position_size = self.total_assets * self.position_size_pct
        print(f"Initial Capital: {self.initial_capital}, Total Assets: {self.total_assets}, Position Size: {position_size}")

        return {
            'initial_cash': self.initial_capital,
            'total_assets': self.total_assets,
            'profit': profit,
            'profit_pct': (profit / self.initial_capital) * 100 if self.initial_capital else 0,
            'equity': strategy_instance.equity,
            'position_size': position_size
        }