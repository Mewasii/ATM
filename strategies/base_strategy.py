from abc import ABC, abstractmethod
import backtrader as bt
import pandas as pd  # Thêm dòng này

# Tạo metaclass tùy chỉnh kế thừa từ cả bt.MetaStrategy và abc.ABCMeta
class StrategyMeta(bt.MetaStrategy, type(ABC)):
    pass

class BaseStrategy(bt.Strategy, ABC, metaclass=StrategyMeta):
    """Lớp cơ sở cho tất cả các chiến lược backtrader."""
    
    @abstractmethod
    def __init__(self):
        """Khởi tạo các chỉ báo và biến cần thiết."""
        pass
    
    @abstractmethod
    def next(self):
        """Logic xử lý từng nến."""
        pass
    
    @abstractmethod
    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Tính toán tín hiệu mua/bán cho DataFrame."""
        pass