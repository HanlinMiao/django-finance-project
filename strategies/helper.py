from .models import Strategy, Trade
from  yahoo_fin import stock_info as si

BLANK_CHOICE = [("-----", "")]

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def portfolio_input():
    global portfolio_size
    portfolio_size = input("Enter the size of your portfolio:")
    
    try:
        float(portfolio_size)
    except ValueError:
        print("That is not a number! \nPlease try again:")
        portfolio_size = input("Enter the size of your portfolio:")

def get_all_strategies():
    result = []
    for strategy in Strategy.objects.order_by("name"):
        result.append(strategy)
    return result

def get_all_trades():
    result = []
    for trade in Trade.objects.order_by("portfolio_size"):
        result.append(trade)
    return result

def get_strategy_choices():
    iquery = Strategy.objects.all()
    iquery_choices = BLANK_CHOICE
    for strategy in iquery:
        iquery_choices += [(Strategy.objects.get(id=strategy.id), strategy.name)]
    return iquery_choices

def call_yahoo_finance_api():
    dic = {}
    dic["Dow Jones"] = si.tickers_dow()
    dic["S&P 500"] = si.tickers_sp500()[:100]
    dic["NASDAQ"] = si.tickers_nasdaq()[:100]

    return dic

from django.template.defaulttags import register
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)