import pandas as pd
<<<<<<< HEAD
from strategies.strategy_registry import StrategyRegistry
=======
>>>>>>> 3e95001d155b8818d7e9738e1787a78c1356edfc

class BacktestAgent:
    def __init__(self, df=None):
        """
        Initialize BacktestAgent with an optional DataFrame.
        Args:
            df: DataFrame with price data (default None)
        """
        self.df = df.copy() if df is not None else None

<<<<<<< HEAD
    def run_backtest(self, strategy="ema_crossover", initial_cash=100000, commission=0.001):
        data = bt.feeds.PandasData(dataname=self.df, datetime='open_time')
        cerebro = bt.Cerebro()
        
        # Lấy chiến lược từ registry
        strategy_class = StrategyRegistry.get_strategy(strategy)
        cerebro.addstrategy(strategy_class)
        
        cerebro.adddata(data)
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=commission)

        # Chạy backtest
        strats = cerebro.run()
        strategy_instance = strats[0]  # Lấy instance của strategy

        # Lấy kết quả
        final_value = cerebro.broker.getvalue()
        profit = final_value - initial_cash
        return {
            'initial_cash': initial_cash,
            'final_value': final_value,
            'profit': profit,
            'profit_pct': (profit / initial_cash) * 100,
            'equity': strategy_instance.equity
        }
=======
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
>>>>>>> 3e95001d155b8818d7e9738e1787a78c1356edfc
