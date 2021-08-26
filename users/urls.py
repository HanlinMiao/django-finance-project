from django.contrib.auth import views as auth_views
from django.urls import path
from .views import (
    register,
    profile,
    user_stock_dashboard,
    add_stock_to_watchlist,
    remove_stock_from_watchlist,
)

urlpatterns = [
    path('register/', register, name ='register'),
    path('profile/', profile, name ='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name ='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name = 'users/logout.html'), name ='logout'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name = 'users/password_reset.html'), 
         name ='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name = 'users/password_reset_done.html'), 
         name ='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name = 'users/password_reset_confirm.html'), 
         name ='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name = 'users/password_reset_complete.html'), 
         name ='password_reset_complete'),
     path('<str:username>/user-stock-dashboard/', user_stock_dashboard, name='user-stock-dashboard'),
     path('<str:username>/<str:stock>/add-stock', add_stock_to_watchlist, name='user-add-stock'),
     path('<str:username>/<str:stock>/remove-stock', remove_stock_from_watchlist, name='user-remove-stock')
]