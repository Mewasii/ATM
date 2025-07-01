import backtrader as bt
import pandas as pd

class EMACrossoverStrategy(bt.Strategy):
    params = (
        ('fast_length', 9),
        ('slow_length', 21),
    )

    def __init__(self):
        self.fast_ema = bt.indicators.EMA(self.data.close, period=self.params.fast_length)
        self.slow_ema = bt.indicators.EMA(self.data.close, period=self.params.slow_length)
        self.equity = []  # Lưu lịch sử equity

    def next(self):
        self.equity.append(self.broker.getvalue())

        if self.fast_ema[0] > self.slow_ema[0] and self.fast_ema[-1] <= self.slow_ema[-1]:
            self.buy()
        elif self.fast_ema[0] < self.slow_ema[0] and self.fast_ema[-1] >= self.slow_ema[-1]:
            self.sell()

class BacktestAgent:
    def __init__(self, df):
        self.df = df.copy()

    def run_backtest(self, strategy="ema_crossover", initial_cash=100000, commission=0.001):
        data = bt.feeds.PandasData(dataname=self.df, datetime='open_time')
        cerebro = bt.Cerebro()
        cerebro.addstrategy(EMACrossoverStrategy)
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
