from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django import forms
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
            exitstatus = process.poll() 
            if (exitstatus==0): 
                    result = {"status": "Success", "output":str(output)} 
            else: 
                    result = {"status": "Failed", "output":str(output)} 

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
    return render(request, "strategies/home.html", {"strategies": strategies, "stocks": stocks})

def live_view(request, stock):
    strategies = get_all_strategies()
    return render(request, "strategies/plot.html", {"strategies": strategies, "stock": stock})


def get_live_price(request, stock):
    if request.method == 'GET': 
        price = si.get_live_price(stock)
        response_data = {}
        response_data['price'] = price
        return JsonResponse(response_data)

