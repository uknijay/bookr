from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm

def discover(request):
    return render(request, "main/events/discover.html")

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('discover')
    else:
        form = LoginForm()
    return render(request, 'main/account/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('discover')
