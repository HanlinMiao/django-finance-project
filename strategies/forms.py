from django import forms
from .models import Trade, Strategy
from .helper import get_strategy_choices, BLANK_CHOICE

class TradeCreateForm(forms.ModelForm):
    tickers = forms.FileField(required=True, help_text="Please upload a .cvs file with all the stock tickers that you are interested in")
    portfolio_size = forms.FloatField(required=True, help_text="Enter your portfolio size in dollars")
    trading_strategy = forms.ModelChoiceField(queryset=Strategy.objects.all(), to_field_name="name", required=True, help_text="Pick a strategy that you think it's appropriate")

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
    