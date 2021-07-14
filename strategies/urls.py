from django.urls import path
from .views import (
    index,
    StrategyCreateView,
    StrategyListView,
    TradeCreateView,
    TradeDetailView,
    TradeListView,
    StrategyDetailView,
    StrategyListView,
    execute_trading_script,
    get_recommended_trade,
    # strategy_create,
)

urlpatterns = [
    path('', index, name="index"),
    path('strategy/', StrategyListView.as_view(), name="strategy-list"),
    path('strategy/<int:pk>/', StrategyDetailView.as_view(), name='strategy-detail'),
    path('strategy/new/', StrategyCreateView.as_view(), name ='strategy-create'),
    path('trade/', TradeListView.as_view(), name ='trade-list'),
    path('trade/new/', TradeCreateView.as_view(), name ='trade-create'),
    path('trade/<int:pk>/', TradeDetailView.as_view(), name='trade-detail'),
    path('trade/<int:pk>/execute/', execute_trading_script, name='execute-script'),
    path('trade/<int:pk>/excel/', get_recommended_trade, name='get-trade'),
]