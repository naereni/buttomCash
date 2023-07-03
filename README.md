# buttomCash
Algo traiding on binance futures

## Download data
To get full orderbook from binance you can use func ```collect_orderbook``` from *parser_orederbook.py* with args:
- save_dir: Path
- mode: [klines/aggTrades/bookTicker/...]
- symbol: [BTCUSDT/LTCUSDT/ADABNB/...]
- timing:  [1m .. 1mo]
- start_date: date of first trade day (required for first collect)
