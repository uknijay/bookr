from django.utils import timezone
from .models import Event, Customer, Books
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from .decorators import *
from main.models import EventPhoto, Account
from .decorators import *
from main.models import EventPhoto, Account
from .forms import LoginForm
from datetime import datetime
from django.db.models import Q


## NOTE: Look at /decorators.py, can use these to check if user is logged in and allow only logged in user to access view. 
##       This is good for like "create event", "rate business", "book event" etc, 



def discover(request):
    events = Event.objects.all()
    return render(request, "main/events/discover.html", {
        "events": events,
    })

def contact(request):
    return render(request, "main/static_pages/contact.html")

def user_login(request):
    if request.session.get('accountId'):
        return redirect("discover")
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():

            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            rememberMe = form.cleaned_data.get('remember_me')

            try:
                account = Account.objects.get(email=email)
                # cant use authenticate since our account is different from djangos built in.
                if check_password(password, account.password):

                    request.session["accountId"] = account.id
                    request.session["accountType"] = account.accountType
                    request.session["accountEmail"] = account.email

                    if not rememberMe:
                        request.session.set_expiry(0)
                    else:
                        request.session.set_expiry(2592000) # 30 days

                    return redirect('discover')
                else:
                    raise Account.DoesNotExist # raise exception to catch below
                
            except Account.DoesNotExist:
                form.add_error(None, "Invalid email or password") # Used if account doesnt exist or invalid combination   
    else:
        form = LoginForm()

    return render(request, 'main/account/login.html', {'form': form})

def user_logout(request):
    request.session.flush()
    return redirect('discover')

def event_detail(request, event_id):

    event =  get_object_or_404(Event, id=event_id)
    eventPhotos = EventPhoto.objects.filter(event=event)


    daysUntilStart = 0
    if event.date:
        today = timezone.now().date()
        start_date = event.date.date()
        daysUntilStart = (start_date - today).days
        if daysUntilStart < 0:
            daysUntilStart = 0


    capacityPercent = 0
    if event.maxCapacity and event.maxCapacity > 0:
        capacityPercent = int((event.currentCapacity / event.maxCapacity) * 100)
        if capacityPercent < 0:
            capacityPercent = 0
        if capacityPercent > 100:
            capacityPercent = 100

    return render(request, "main/events/detail.html", {
        "event": event,
        "eventPhotos": eventPhotos,
        "daysUntilStart": daysUntilStart,
        "capacityPercent": capacityPercent,
    })

@customer_required #Decorator handles checking if user logged in and is customer, if not logged in --> /login, if not customer --> /discover
def book_event(request, event_id):
    if request.method != "POST":
        return redirect("event_detail", event_id=event_id)

    event =  get_object_or_404(Event, id=event_id)
    customer = get_object_or_404(Customer, accountId=request.session.get("accountId"))

    if Books.objects.filter(customerId=customer, eventId=event).exists():
        messages.warning(request, "User already booked this event")
        return redirect("event_detail", event_id=event_id)

    try:
        booking = Books(customerId=customer, eventId=event)
        booking.save()
        messages.success(request, "Booking created successfully.")
        
    except Exception as e:
        messages.error(request, str(e))

    return redirect("event_detail", event_id=event_id)

def about(request):
    return render(request, "main/static_pages/about.html")



