from pyexpat.errors import messages

from django.utils import timezone
from .models import Account, Books, Customer, Event

from django.http import HttpResponse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from main.models import EventPhoto

from main.models import EventPhoto
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

def event_detail(request, event_id):

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return HttpResponse("Event not found", status=404)


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

@login_required
def book_event(request, event_id):
    if request.method != "POST":
        return redirect("event_detail", event_id=event_id)

    event =  get_object_or_404(Event, id=event_id)

    try:
        account = Account.objects.get(email=request.user.email)
        customer = Customer.objects.get(accountId=account)

    except Account.DoesNotExist:

        messages.error(request, "User does not exist")
        return redirect("event_detail", event_id=event_id)
    
    except Customer.DoesNotExist:
        messages.error(request, "Customer profile not found")
        return redirect("event_detail", event_id=event_id)

    if Books.objects.filter(customerId=customer, eventId=event).exists():
        messages.warning(request, "User already booked this event")
        return redirect("event_detail", event_id=event_id)

    try:
        Books.objects.create(customerId=customer, eventId=event)
        messages.success(request, "Booking created successfully.")
        
    except Exception as e:
        messages.error(request, str(e))

    return redirect("event_detail", event_id=event_id)

