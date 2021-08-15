import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math
from secrets import IEX_CLOUD_API_TOKEN
import sys, getopt


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def main(argv):
    ticker_file = ""
    portfolio_size = 0
    trade_id = -1
    try:
      opts, args = getopt.getopt(argv,"hc:p:t:",["csv=","portfolio=","trade_id="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('test_script.py -c <csv_file> -p <portfolio_size> -t <trade_id>')
            sys.exit()
        elif opt in ("-c", "--csv"):
            ticker_file = arg
        elif opt in ("-p", "--portfolio"):
            portfolio_size = float(arg)
        elif opt in ("-t", "--trade_id"):
            trade_id = arg

    stocks = pd.read_csv(ticker_file)
    my_columns = ["Ticker", "Stock Price", "Market Capitalization", "Number of Shares to Buy"]
    final_dataframe = pd.DataFrame(columns=my_columns)
    final_dataframe.append(
        pd.Series(
        [
            symbol,
            price,
            market_cap,
            "N/A"
        ],
        index = my_columns,
        ),
        ignore_index = True
    )
    final_dataframe = pd.DataFrame(columns = my_columns)
    for stock in stocks["Ticker"]:
        api_url = f"https://sandbox.iexapis.com/stable/stock/{stock}/quote/?token={IEX_CLOUD_API_TOKEN}"
        data = requests.get(api_url).json()
        final_dataframe = final_dataframe.append(
            pd.Series(
            [
                stock,
                data["latestPrice"],
                data["marketCap"],
                "N/A"
            ],
            index = my_columns
            ),
            ignore_index = True
        )
    symbol_groups = list(chunks(stocks["Ticker"], 100))
    symbol_strings = []
    for i in range(0, len(symbol_groups)):
        symbol_strings.append(','.join(symbol_groups[i]))
    final_dataframe = pd.DataFrame(columns=my_columns)

    for symbol_string in symbol_strings:
        batch_api_call_url = f"https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}"
        data = requests.get(batch_api_call_url).json()
        for symbol in symbol_string.split(","):
            final_dataframe = final_dataframe.append(
                pd.Series(
                    [
                        symbol,
                        data[symbol]["quote"]["latestPrice"],
                        data[symbol]["quote"]["marketCap"],
                        "N/A"

                    ],
                    index = my_columns,
                ),
                ignore_index=True,
            )
    val = portfolio_size
    position_size = val/len(final_dataframe.index)
    for i in range(0, len(final_dataframe.index)):
        final_dataframe.loc[i, "Number of Shares to Buy"] = math.floor(position_size/final_dataframe.loc[i, "Stock Price"])

    writer = pd.ExcelWriter(f"output_files/recommended_trades_{trade_id}.xlsx", engine="xlsxwriter")
    final_dataframe.to_excel(writer, "Recommended Trades", index=False)

    background_color = "#0a0a23"
    font_color = "#ffffff"

    string_format = writer.book.add_format(
        {
            "font_color": font_color,
            "bg_color": background_color,
            "border": 1,
        }
    )
    dollar_format = writer.book.add_format(
        {
            "num_format": "$0.00",
            "font_color": font_color,
            "bg_color": background_color,
            "border": 1,
        }
    )
    integer_format = writer.book.add_format(
        {
            "num_format": "0",
            "font_color": font_color,
            "bg_color": background_color,
            "border": 1,
        }
    )
    column_formats = {
        "A":["Tickers", string_format] ,
        "B":["Stock Price", dollar_format],
        "C":["Markt Capitalization", dollar_format],
        "D":["Number of Shares to Buy", integer_format],
    }

    for column in column_formats.keys():
        writer.sheets["Recommended Trades"].write(f"{column}1", column_formats[column][0], column_formats[column][1])
        writer.sheets["Recommended Trades"].set_column(f"{column}:{column}", 18, column_formats[column][1])

    writer.save()
    
    
if __name__ == "__main__":
   main(sys.argv[1:])