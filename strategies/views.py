from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import Strategy, Trade
from .helper import chunks, get_all_strategies, get_all_trades
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

class StrategyCreateView(CreateView):
    model = Strategy
    form_class = StrategyCreateForm
    template_name = "strategies/strategy_form.html"

    def get_context_data(self, **kwargs):
        context = super(StrategyCreateView, self).get_context_data(**kwargs)
        context["strategies"] = get_all_strategies()
        return context
    
# def strategy_create(request):
#     print(request.method)
#     if request.method == 'POST':
#         form = StrategyCreateForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('strategy-list')
#     else:
#         form = StrategyCreateForm()
#     return render(request, 'strategies/strategy_form.html', {
#         'form': form
#     })


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

class TradeCreateView(CreateView):
    model = Trade
    form_class = TradeCreateForm
    
    def get_context_data(self, **kwargs):
        context = super(TradeCreateView, self).get_context_data(**kwargs)
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

        html = "<html><body>Script status: %s \n Output: %s</body></html>" %(result['status'],result['output']) 
        return HttpResponse(html)

def get_recommended_trade(request, pk):
    path = f"output_files/recommended_trades_{pk}.xlsx"
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def index(request):
    strategies = get_all_strategies()
    return render(request, "strategies/base.html", {"strategies": strategies})

