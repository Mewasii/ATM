from user_proxy import BinanceUserProxy

def main():
    proxy = BinanceUserProxy()
    proxy.run_workflow(
        symbol="BTCUSDT",
        interval="1h",
        limit=100,
        chart_type="candlestick"
    )

if __name__ == "__main__":
    main()