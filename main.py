import argparse
from user_proxy import BinanceUserProxy
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
def parse_arguments():
    """Phân tích các tham số dòng lệnh."""
    parser = argparse.ArgumentParser(description="Binance Trading Workflow")
    parser.add_argument("--symbol", type=str, default="BTCUSDT", help="Cặp giao dịch (e.g., BTCUSDT)")
    parser.add_argument("--interval", type=str, default="1h", help="Khoảng thời gian (e.g., 1h, 4h, 1d)")
    parser.add_argument("--limit", type=int, default=100, help="Số lượng nến (e.g., 100)")
    parser.add_argument("--chart-type", type=str, default="combined", choices=["candlestick", "line", "combined"],
                        help="Loại biểu đồ (candlestick, line, combined)")
    parser.add_argument("--indicators", type=str, default=None, 
                        help="Danh sách các chỉ báo, cách nhau bởi dấu phẩy (e.g., sma,rsi)")
    parser.add_argument("--strategy", type=str, default=None, 
                        help="Chiến lược backtest (e.g., ema_crossover)")
    
    args = parser.parse_args()
    
    # Xử lý indicators
    indicators = [ind.strip() for ind in args.indicators.split(",")] if args.indicators else None
    
    return args.symbol, args.interval, args.limit, args.chart_type, indicators, args.strategy

def main():
    # Khởi tạo proxy
    proxy = BinanceUserProxy()
    
    # Lấy tham số từ dòng lệnh
    symbol, interval, limit, chart_type, indicators, strategy = parse_arguments()
    
    # Chạy workflow
    try:
        proxy.run_workflow(
            symbol=symbol,
            interval=interval,
            limit=limit,
            chart_type=chart_type,
            indicators=indicators,
            strategy=strategy
        )
    except ValueError as e:
        print(f"Lỗi: {e}")
    except Exception as e:
        print(f"Đã xảy ra lỗi không mong muốn: {e}")

if __name__ == "__main__":
    main()