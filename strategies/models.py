from django.db import models
from django.urls import reverse

class Strategy(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255)
    script = models.FileField(upload_to="strategy_scripts/")

    def get_absolute_url(self):
        return reverse('strategy-detail', kwargs={'pk' : self.pk})
    
    def get_script_lines(self):
        with open (f"{self.script}", "r") as f:    
            content = f.read()
        f.close()
        return content

class Trade(models.Model):
    tickers = models.FileField(upload_to="input_files/")
    portfolio_size = models.FloatField()
    trading_strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('trade-detail', kwargs={'pk' : self.pk})

