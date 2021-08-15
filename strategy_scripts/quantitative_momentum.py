import numpy as np
import sys, getopt
import pandas as pd
import requests
import math
from scipy.stats import percentileofscore as score
from secrets import IEX_CLOUD_API_TOKEN
import xlsxwriter


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
        print ('quantitative_momentum.py -c <csv_file> -p <portfolio_size> -t <trade_id>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('quantitative_momentum.py -c <csv_file> -p <portfolio_size> -t <trade_id>')
            sys.exit()
        elif opt in ("-c", "--csv"):
            ticker_file = arg
        elif opt in ("-p", "--portfolio"):
            portfolio_size = float(arg)
        elif opt in ("-t", "--trade_id"):
            trade_id = arg

    stocks = pd.read_csv(ticker_file)
    symbol_groups = list(chunks(stocks['Ticker'], 100))
    symbol_strings = []
    for i in range(0, len(symbol_groups)):
        symbol_strings.append(','.join(symbol_groups[i]))
    #     print(symbol_strings[i])

    my_columns = ['Ticker', 'Price', 'One-Year Price Return', 'Number of Shares to Buy']

    final_dataframe = pd.DataFrame(columns=my_columns)

    for symbol_string in symbol_strings:
        batch_api_call_url = f"https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=stats,price&token={IEX_CLOUD_API_TOKEN}"
        data = requests.get(batch_api_call_url).json()
        for symbol in symbol_string.split(","):
            final_dataframe = final_dataframe.append(
                pd.Series(
                    [
                        symbol,
                        data[symbol]["price"],
                        data[symbol]["stats"]["year1ChangePercent"],
                        "N/A"
                    ],
                    index = my_columns,
                ),
                ignore_index = True
            )
    final_dataframe.sort_values("One-Year Price Return", ascending=False, inplace=True)
    final_dataframe = final_dataframe[:50]
    final_dataframe.reset_index(inplace=True, drop=True)
    final_dataframe
    val = portfolio_size
    position_size = float(portfolio_size)/len(final_dataframe.index)
    for i in range(0, len(final_dataframe)):
        final_dataframe.loc[i, "Number of Shares to Buy"] = math.floor(position_size/final_dataframe.loc[i, "Price"])
    hqm_columns = [
                'Ticker', 
                'Price', 
                'Number of Shares to Buy', 
                'One-Year Price Return', 
                'One-Year Return Percentile',
                'Six-Month Price Return',
                'Six-Month Return Percentile',
                'Three-Month Price Return',
                'Three-Month Return Percentile',
                'One-Month Price Return',
                'One-Month Return Percentile',
                'HQM Score'
                ]

    hqm_dataframe = pd.DataFrame(columns = hqm_columns)

    for symbol_string in symbol_strings:
        batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
        data = requests.get(batch_api_call_url).json()
        for symbol in symbol_string.split(','):
            hqm_dataframe = hqm_dataframe.append(
                                            pd.Series([symbol, 
                                                    data[symbol]['quote']['latestPrice'],
                                                    'N/A',
                                                    data[symbol]['stats']['year1ChangePercent'],
                                                    'N/A',
                                                    data[symbol]['stats']['month6ChangePercent'],
                                                    'N/A',
                                                    data[symbol]['stats']['month3ChangePercent'],
                                                    'N/A',
                                                    data[symbol]['stats']['month1ChangePercent'],
                                                    'N/A',
                                                    'N/A'
                                                    ], 
                                                    index = hqm_columns), 
                                            ignore_index = True)
    time_periods = [
        "One-Year",
        "Six-Month",
        "Three-Month",
        "One-Month",
    ]
    hqm_dataframe
    hqm_dataframe.fillna(0,inplace=True)


    for row in hqm_dataframe.index:
        for time_period in time_periods:
            change_col = f'{time_period} Price Return'
            percentile_col = f'{time_period} Return Percentile'
            hqm_dataframe.loc[row, percentile_col] = score(hqm_dataframe[change_col], hqm_dataframe.loc[row, change_col])/100
    from statistics import mean

    for row in hqm_dataframe.index:
        momentum_percentiles = []
        for time_period in time_periods:
            momentum_percentiles.append(hqm_dataframe.loc[row, f"{time_period} Return Percentile"])
        hqm_dataframe.loc[row, f"HQM Score"] = mean(momentum_percentiles)
    hqm_dataframe.sort_values("HQM Score", ascending = False, inplace=True)
    hqm_dataframe = hqm_dataframe[:50]
    hqm_dataframe = hqm_dataframe.reset_index(drop=True)

    position_size = float(portfolio_size)/len(hqm_dataframe.index)
    for i in hqm_dataframe.index:
        hqm_dataframe.loc[i, "Number of Shares to Buy"] = math.floor(position_size/hqm_dataframe.loc[i, "Price"])


    writer = pd.ExcelWriter(f"output_files/recommended_trades_{trade_id}.xlsx", engine="xlsxwriter")
    hqm_dataframe.to_excel(writer, sheet_name = "Momentum Strategy", index = False)


    background_color = '#0a0a23'
    font_color = '#ffffff'

    string_template = writer.book.add_format(
            {
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )

    dollar_template = writer.book.add_format(
            {
                'num_format':'$0.00',
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )

    integer_template = writer.book.add_format(
            {
                'num_format':'0',
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )

    percent_template = writer.book.add_format(
            {
                'num_format':'0.0%',
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )
    column_formats = {
        'A':['Ticker', string_template], 
        'B':['Price', dollar_template], 
        'C':['Number of Shares to Buy', integer_template], 
        'D':['One-Year Price Return', percent_template], 
        'E':['One-Year Return Percentile', percent_template],
        'F':['Six-Month Price Return', percent_template],
        'G':['Six-Month Return Percentile', percent_template],
        'H':['Three-Month Price Return', percent_template],
        'I':['Three-Month Return Percentile', percent_template],
        'J':['One-Month Price Return', percent_template],
        'K':['One-Month Return Percentile', percent_template],
        'L':['HQM Score', percent_template]
    }

    for column in column_formats.keys():
        writer.sheets["Momentum Strategy"].set_column(f"{column}:{column}", 25, column_formats[column][1])
        writer.sheets["Momentum Strategy"].write(f"{column}1", column_formats[column][0], column_formats[column][1])

    writer.save()
    
    
if __name__ == "__main__":
   main(sys.argv[1:])