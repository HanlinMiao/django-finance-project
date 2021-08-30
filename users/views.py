from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, StockUpdateForm
from .models import Profile, User


def register(request):
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, f'Your account has been created! You are now able to login')
			return redirect('login')
	else:
		form = UserRegisterForm()
	return render(request, 'users/register.html', {'form':form})

@login_required
def profile(request):
	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST, instance = request.user)
		p_form = ProfileUpdateForm(request.POST, request.FILES, instance = request.user.profile)
		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			messages.success(request, f'Your account has been updated!')
			return redirect('profile')
		
	else:
		u_form = UserUpdateForm(instance = request.user)
		p_form = ProfileUpdateForm(instance = request.user.profile)

	context = {
			'u_form': u_form,
			'p_form': p_form
		}

	return render(request, 'users/profile.html', context)

@login_required
def user_stock_dashboard(request, username):
	user = User.objects.get(username=username)
	profile = Profile.objects.get(user=user)
	stocks = profile.get_stocks().split(",")
	context = {
		"user": user,
		"stocks": sorted(stocks),
		"interval": "yearly"
	}

	return render(request, 'users/track_stocks.html', context)

@login_required
def add_stock_to_watchlist(request, username, stock):
	user = User.objects.get(username=username)
	profile = Profile.objects.get(user=user)
	watch_list = profile.stocks.split(",")
	if stock in watch_list:
		messages.warning(request, f'{stock} is already in your watchlist')
		return redirect('index')
	else:
		profile.stocks += ("," + stock)
		profile.save()
		watch_list.append(stock)
		messages.success(request, f'{stock} has been added to your watchlist')
	
	context = {
		"user": user,
		"stocks": sorted(watch_list),
	}

	return redirect('user-stock-dashboard', user)

def remove_stock_from_watchlist(request, username, stock):
	user = User.objects.get(username=username)
	profile = Profile.objects.get(user=user)
	watch_list = profile.stocks.split(",")
	if stock not in watch_list:
		messages.warning(request, f'This stock {stock} is not in your watchlist')
		return redirect('index')
	else:
		watch_list.remove(stock)
		profile.stocks = ",".join(watch_list)
		profile.save()
		messages.success(request, f'{stock} has been removed from your watchlist')
	
	context = {
		"user": user,
		"stocks": sorted(watch_list),
	}

	return redirect('user-stock-dashboard', user)

	
	


"""
messages.debug
messages.info
messages.success
messages.warning
messages.error
"""