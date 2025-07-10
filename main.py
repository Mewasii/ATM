import argparse
from agents.historical_data_agent import HistoricalDataAgent
from agents.chart_agent import ChartAgent
from agents.strategy_agent import StrategyAgent
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run HistoricalDataAgent and ChartAgent for data collection and visualization.")
    parser.add_argument('--symbol', default='BTCUSDT', help='Trading pair symbol (e.g., BTCUSDT)')
    parser.add_argument('--interval', default='1h', help='Kline interval (e.g., 1h, 1d)')
    parser.add_argument('--start-date', default='2019-01-01', help='Start date for historical data (YYYY-MM-DD)')
    parser.add_argument('--limit', type=int, default=1000, help='Limit of klines per request (max 1000)')
    parser.add_argument('--websocket', action='store_true', help='Enable WebSocket for real-time updates')
    parser.add_argument('--chart-type', default='combined', choices=['combined', 'candlestick', 'line'], help='Chart type (combined, candlestick, line)')
    parser.add_argument('--indicators', default='sma,rsi', help='Comma-separated list of indicators (e.g., sma,rsi)')
    parser.add_argument('--strategy', default='ema_crossover', help='Trading strategy (e.g., ema_crossover)')
    args = parser.parse_args()

    # Initialize HistoricalDataAgent
    agent = HistoricalDataAgent(symbol=args.symbol, interval=args.interval)
    
    # Collect historical data if CSV doesn't exist
    data_file = os.path.join("data/raw", f"{args.symbol}_{args.interval}.csv")
    if not os.path.exists(data_file):
        logger.info(f"Starting historical data collection for {args.symbol} at {args.interval} from {args.start_date}")
        agent.collect_historical_data(start_date=args.start_date)
    
    # Start WebSocket if enabled
    if args.websocket:
        logger.info("Starting WebSocket for real-time updates")
        agent.start_websocket()

    # Initialize ChartAgent
    chart_agent = ChartAgent()
    
    # Parse indicators
    indicators = args.indicators.split(',') if args.indicators else []

    # Plot chart based on chart-type
    if args.chart_type == 'combined':
        logger.info(f"Generating combined chart for {args.symbol} with indicators {indicators} and strategy {args.strategy}")
        fig = chart_agent.plot_combined_charts(
            data_file=data_file,
            symbol=args.symbol,
            interval=args.interval,
            indicators=indicators,
            strategy=args.strategy,
            chart_type='heikin_ashi' if 'heikin_ashi' in args.chart_type.lower() else 'normal',
            save=True
        )
        fig.show()
    elif args.chart_type == 'candlestick':
        logger.info(f"Generating candlestick chart for {args.symbol}")
        fig = chart_agent.plot_candlestick(data_file=data_file, symbol=args.symbol, save=True)
        fig.show()
    elif args.chart_type == 'line':
        logger.info(f"Generating line chart for {args.symbol}")
        fig = chart_agent.plot_line(data_file=data_file, symbol=args.symbol, save=True)
        fig.show()

    # Keep WebSocket running if enabled
    if args.websocket:
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logger.info("Stopping WebSocket and exiting...")
            agent.stop_websocket()

if __name__ == "__main__":
    main()