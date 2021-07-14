from django import forms
from .models import Trade, Strategy
from .helper import get_strategy_choices, BLANK_CHOICE

class TradeCreateForm(forms.ModelForm):
    tickers = forms.FileField(required=True)
    portfolio_size = forms.FloatField(required=True)
    trading_strategy = forms.ModelChoiceField(queryset=Strategy.objects.all(), required=True)

    class Meta:  
        model = Trade
        fields = ["tickers", "portfolio_size", "trading_strategy"]

class StrategyCreateForm(forms.ModelForm):
    script = forms.FileField(required=True)
    name = forms.CharField(required=True)
    description = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = Strategy
        fields = ["script", "name", "description"]
    