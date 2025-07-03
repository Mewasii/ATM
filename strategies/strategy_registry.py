from strategies.ema_crossover import EMACrossoverStrategy

class StrategyRegistry:
    _strategies = {
        "ema_crossover": EMACrossoverStrategy,
        # Thêm các chiến lược khác ở đây, ví dụ:
        # "other_strategy": OtherStrategy,
    }

    @classmethod
    def get_strategy(cls, strategy_name):
        """Lấy chiến lược theo tên."""
        strategy = cls._strategies.get(strategy_name.lower())
        if not strategy:
            raise ValueError(f"Chiến lược '{strategy_name}' không tồn tại.")
        return strategy

    @classmethod
    def register_strategy(cls, name, strategy_class):
        """Đăng ký một chiến lược mới."""
        cls._strategies[name.lower()] = strategy_class