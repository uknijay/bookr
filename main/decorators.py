from django.shortcuts import redirect
from functools import wraps

def account_required(view_func):
    #Decorator to ensure ANY user (customer or business) is logged in
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('accountId'):
            return redirect('login')  # Redirect to login 
        return view_func(request, *args, **kwargs)
    return wrapper

def customer_required(view_func):
    # Decorator to ensure ONLY customers can access the view.
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('accountId'):
            return redirect('login')
        if request.session.get('accountType') != 'customer':
            return redirect('discover') 
        return view_func(request, *args, **kwargs)
    return wrapper

def business_required(view_func):
    # Decorator to ensure ONLY businesses can access the view.
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('accountId'):
            return redirect('login')
        if request.session.get('accountType') != 'business':
            return redirect('discover')
        return view_func(request, *args, **kwargs)
    return wrapper
