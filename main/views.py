from django.utils import timezone
from .models import Event

from django.http import HttpResponse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from main.models import EventPhoto

from main.models import EventPhoto
from .forms import LoginForm, RegistrationForm

def discover(request):
    return render(request, "main/events/discover.html")

def contact(request):
    return render(request, "main/static_pages/contact.html")

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

def about(request):
    return render(request, "main/static_pages/about.html")

def register_view(request):
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("profile")
    else:
        form = RegistrationForm()

    return render(request, "main/account/register.html", {"form": form})


@login_required
def profile_view(request):
    return render(request, "main/account/profile.html")
