from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django import forms
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from .models import Strategy, Trade
from .helper import call_yahoo_finance_api, chunks, get_all_strategies, get_all_trades
from .format import (
    background_color,
    font_color,
    string_format,
    dollar_format,
    integer_format,
)
from .forms import TradeCreateForm, StrategyCreateForm
from .secrets import IEX_CLOUD_API_TOKEN
from subprocess import Popen, PIPE, STDOUT
import os
from  yahoo_fin import stock_info as si
import yfinance as yf
from datetime import date, timedelta, datetime
from django.urls import reverse
from urllib.parse import urlencode


class StrategyCreateView(CreateView):
    model = Strategy
    form_class = StrategyCreateForm
    template_name = "strategies/strategy_form.html"

    def get_context_data(self, **kwargs):
        context = super(StrategyCreateView, self).get_context_data(**kwargs)
        context["strategies"] = get_all_strategies()
        return context

class StrategyEditView(UpdateView):
    model = Strategy
    form_class = StrategyCreateForm
    template_name = "strategies/strategy_edit.html"

    def get_context_data(self, **kwargs):
        context = super(StrategyEditView, self).get_context_data(**kwargs)
        context["strategies"] = get_all_strategies()
        return context

class StrategyListView(ListView):
    model = Strategy
    template_name = 'strategies/strategy_list.html'

    def get_context_data(self, **kwargs):
        context = super(StrategyListView, self).get_context_data(**kwargs)
        context["strategies"] = get_all_strategies()
        return context

class StrategyDetailView(DetailView):
    model = Strategy
    template_name = 'strategies/strategy_detail.html'

    def get_context_data(self, **kwargs):
        context = super(StrategyDetailView, self).get_context_data(**kwargs)
        context["strategies"] = get_all_strategies()
        return context

class StrategyDeleteView(DeleteView):
    model = Strategy
    template_name = 'strategies/strategy_delete.html'
    success_url = reverse_lazy('strategy-list')

    def get_context_data(self, **kwargs):
        context = super(StrategyDetailView, self).get_context_data(**kwargs)
        context["strategies"] = get_all_strategies()
        return context

class TradeCreateView(CreateView):
    model = Trade
    form_class = TradeCreateForm
    template = 'strategies/trade_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super(TradeCreateView, self).get_context_data(**kwargs)
        context["strategies"] = get_all_strategies()
        return context
    
class TradeEditView(UpdateView):
    model = Trade
    form_class = TradeCreateForm
    template_name = "strategies/trade_edit.html"
    
    def get_context_data(self, **kwargs):
        context = super(TradeEditView, self).get_context_data(**kwargs)
        context["strategies"] = get_all_strategies()
        return context

class TradeDetailView(DetailView):
    model = Trade

    def get_context_data(self, **kwargs):
        context = super(TradeDetailView, self).get_context_data(**kwargs)
        context["strategies"] = get_all_strategies()
        return context

class TradeListView(ListView):
    model = Trade
    template_name = 'strategies/trade_list.html'

    def get_context_data(self, **kwargs):
        context = super(TradeListView, self).get_context_data(**kwargs)
        context["strategies"] = get_all_strategies()
        context["trades"] = get_all_trades()
        return context

class TradeDeleteView(DeleteView):
    model = Trade
    template_name = 'strategies/trade_delete.html'
    success_url = reverse_lazy('trade-list')

    def get_context_data(self, **kwargs):
        context = super(TradeDeleteView, self).get_context_data(**kwargs)
        context["strategies"] = get_all_strategies()
        context["trades"] = get_all_trades()
        return context

def script_loading(request, pk):
    strategies = get_all_strategies()
    trade = Trade.objects.get(pk=pk)
    return render(request, "strategies/script_result.html", {"strategies": strategies, "trade": trade})

def execute_trading_script(request, pk):
    trade = Trade.objects.get(pk=pk)
    trade_id = trade.pk
    script = trade.trading_strategy.script
    csv_file = str(trade.tickers).strip()
    portfolio_size = trade.portfolio_size
    if request.method == 'GET': 
        command = ["python3", f"{script}", f"-c{csv_file}", f"-p{portfolio_size}", f"-t{trade_id}"] 
        try: 
            process = Popen(command, stdout=PIPE, stderr=STDOUT) 
            output = process.stdout.read()
            output = str(output).split("\\n")
            output = "\n".join(output)
            exitstatus = process.poll() 
            if (exitstatus==0): 
                    result = {"status": "Success", "output":output} 
            else: 
                    result = {"status": "Failed", "output":output} 

        except Exception as e: 
            result =  {"status": "failed", "output":str(e)} 

        response_data = {}
        response_data['status'] = result['status']
        response_data['output'] = result['output']
        return JsonResponse(response_data)

def get_recommended_trade(request, pk):
    path = f"recommended_trades_{pk}.xlsx"
    file_path = os.path.join(settings.OUTPUT_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def download_ticker_file(request, pk):
    trade = Trade.objects.get(pk=pk)
    tickers = trade.tickers
    path = f"{tickers}"
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def download_script(request, pk):
    strategy = Strategy.objects.get(pk=pk)
    script = strategy.script
    path = f"{script}"
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def index(request):
    strategies = get_all_strategies()
    stocks = call_yahoo_finance_api()
    interval = "daily"
    return render(request, "strategies/home.html", {"strategies": strategies, "stocks": stocks, "interval": interval})

def search_stock(request):
    if request.GET.get('q', False):
        stock = request.GET.get('q', False)
        if live_view(request, stock) == "No Data Available":
            messages.info(request, f'{stock} data not available at this moment')
            return redirect('search-stock')
        else:
            return redirect('stock-price', stock)

    strategies = get_all_strategies()
    return render(request, "strategies/search_stock.html", {"strategies": strategies})

def live_view(request, stock):
    strategies = get_all_strategies()
    data = yf.download(tickers=stock, period="1d", interval="1m")
    if data.empty:
        return "No Data Available"
    dps = data['Adj Close']
    dic = []
    for index, value in dps.items():
        dic.append(value)
    return render(request, "strategies/live_prices.html", {"strategies": strategies, "stock": stock, "dps": dic})

def get_live_price(request, stock):
    if request.method == 'GET':
        price = si.get_live_price(stock)
        time = datetime.now() - timedelta(hours=4)
        time = time.strftime("%H:%M")
        response_data = {}
        response_data['price'] = price
        response_data['time'] = time
        return JsonResponse(response_data)

def historical_chart(request, stock, interval):
    strategies = get_all_strategies()
    return render(request, "strategies/historical_prices.html", {"strategies": strategies, "stock": stock, "interval": interval})

def get_historical_price(request, stock, interval):
    """Populate Line Chart Data."""
    labels = []
    # Get Financial Data
    if interval == "" or interval == "daily":
        interval = "1d"
        days = 30
    elif interval == "weekly":
        interval = "1wk"
        days = 60
    elif interval == "monthly":
        interval = "1mo"
        days = 365
    else:
        interval = "1mo"
        days = 365 * 3
    start_date = str((date.today() - timedelta(days=days)).strftime("%m/%d/%Y"))
    end_date = str(date.today().strftime("%m/%d/%Y"))
    data = si.get_data(stock, start_date=start_date, end_date=end_date, interval=interval)
    table = si.get_quote_table(stock)

    for time in data.dropna().index:
        labels.append(time.strftime("%m/%d/%Y"))
    response_data = {}
    response_data['labels'] = labels
    response_data['data'] = list(data.dropna().adjclose)
    response_data['open'] = '{:.2f}'.format(float(data[-1:]['open']))
    response_data['close'] = '{:.2f}'.format(float(data[-1:]['close']))
    response_data['adjclose'] = '{:.2f}'.format(float(data[-1:]['adjclose']))
    try:
        response_data['volume'] = int(data[-1:]['volume'])
    except ValueError:
        response_data['volume'] = "NaN"
    
    response_data['marketcap'] = table['Market Cap']
    response_data['avgvol'] = table['Avg. Volume']
    range = table['52 Week Range']
    response_data['high'] = range[range.index('-')+1:]
    response_data['low'] = range[:range.index('-')]
    response_data['dividend'] = table['Forward Dividend & Yield']
    response_data['pe'] = str(table['PE Ratio (TTM)'])

    return JsonResponse(response_data)
