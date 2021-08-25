from  yahoo_fin import stock_info as si

choices = []
tickers = si.tickers_dow()
for i in range(len(list(tickers))):
    choices.append((i, tickers[i]))