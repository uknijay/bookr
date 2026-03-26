import datetime
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from .models import Account, Business, Event, EventPhoto, Books, Rates
from .forms import LoginForm, EventForm

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


def business_my_events(request):
    # Simple unsupported auth mapping: use matched Business by account email or first business.
    business = None
    if request.user.is_authenticated and hasattr(request.user, "email"):
        business = Business.objects.filter(account__email=request.user.email).first()
    if business is None:
        business = Business.objects.first()

    if business is None:
        return HttpResponse("No business profile found. Create a business first.", status=404)

    now = timezone.now()
    upcomingEvents = list(business.organised_events.filter(date__gte=now).order_by("date"))
    pastEvents = list(business.organised_events.filter(date__lt=now).order_by("-date"))

    totalBookings = sum(event.totalBookings for event in upcomingEvents + pastEvents)
    spotsRemaining = sum(max(0, event.maxCapacity - event.currentCapacity) for event in upcomingEvents)
    totalSpots = sum(event.maxCapacity for event in upcomingEvents)
    spotsBooked = sum(event.currentCapacity for event in upcomingEvents)
    spotsBookedPercent = int((spotsBooked / totalSpots) * 100) if totalSpots > 0 else 0

    return render(request, "main/business/my_events.html", {
        "business": business,
        "upcomingEvents": upcomingEvents,
        "pastEvents": pastEvents,
        "upcomingEventCount": len(upcomingEvents),
        "totalBookings": totalBookings,
        "spotsRemaining": spotsRemaining,
        "spotsBookedPercent": spotsBookedPercent,
    })


def get_current_business(request):
    if request.user.is_authenticated and hasattr(request.user, 'email'):
        business = Business.objects.filter(account__email=request.user.email).first()
        if business:
            return business

    return Business.objects.first()


def business_dashboard(request):
    business = get_current_business(request)
    if business is None:
        return HttpResponse("No business account found", status=404)

    now = timezone.now()
    upcomingEvents = list(business.organised_events.filter(date__gte=now).order_by('date'))
    pastEvents = list(business.organised_events.filter(date__lt=now).order_by('-date'))
    totalBookings = sum(event.totalBookings for event in upcomingEvents + pastEvents)
    spotsRemaining = sum(max(0, event.maxCapacity - event.currentCapacity) for event in upcomingEvents)

    return render(request, 'main/business/dashboard.html', {
        'business': business,
        'upcomingEvents': upcomingEvents,
        'pastEvents': pastEvents,
        'upcomingEventCount': len(upcomingEvents),
        'totalBookings': totalBookings,
        'spotsRemaining': spotsRemaining,
    })


def business_event_stats(request, event_id):
    business = get_current_business(request)
    if business is None:
        return HttpResponse("No business account found", status=404)

    event = Event.objects.filter(id=event_id, organiser=business).first()
    if event is None:
        return HttpResponse("Event not found", status=404)

    rates = Rates.objects.filter(businessId=business)
    return render(request, 'main/business/event_stats.html', {
        'business': business,
        'event': event,
        'ratings': rates,
    })


def business_view_ratings(request):
    business = get_current_business(request)
    if business is None:
        return HttpResponse("No business account found", status=404)

    ratings = Rates.objects.filter(businessId=business)
    return render(request, 'main/business/view_ratings.html', {
        'business': business,
        'ratings': ratings,
    })


def business_past_events(request):
    business = get_current_business(request)
    if business is None:
        return HttpResponse("No business account found", status=404)

    now = timezone.now()
    pastEvents = business.organised_events.filter(date__lt=now).order_by('-date')
    return render(request, 'main/business/past_events.html', {
        'business': business,
        'pastEvents': pastEvents,
    })


def business_upcoming_events(request):
    business = get_current_business(request)
    if business is None:
        return HttpResponse("No business account found", status=404)

    now = timezone.now()
    upcomingEvents = business.organised_events.filter(date__gte=now).order_by('date')
    return render(request, 'main/business/my_events.html', {
        'business': business,
        'upcomingEvents': upcomingEvents,
        'pastEvents': [],
        'upcomingEventCount': upcomingEvents.count(),
        'totalBookings': sum([event.totalBookings for event in upcomingEvents]),
        'spotsRemaining': sum(max(0, event.maxCapacity - event.currentCapacity) for event in upcomingEvents),
        'spotsBookedPercent': int((sum(event.currentCapacity for event in upcomingEvents) / max(1, sum(event.maxCapacity for event in upcomingEvents))) * 100) if upcomingEvents.exists() else 0,
    })


def business_create_event(request):
    business = get_current_business(request)
    if business is None:
        return HttpResponse("No business account found", status=404)

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            max_capacity = form.cleaned_data['maxCapacity']
            event = Event.objects.create(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                venue=form.cleaned_data['venue'],
                venueAddress=form.cleaned_data['venueAddress'],
                date=timezone.make_aware(datetime.datetime.combine(date, time)),
                maxCapacity=max_capacity,
                currentCapacity=0,
                organiser=business,
            )

            for photo in request.FILES.getlist('photos'):
                EventPhoto.objects.create(event=event, image=photo)

            return redirect('business_my_events')
    else:
        form = EventForm()

    return render(request, 'main/business/create_event.html', {
        'business': business,
        'form': form,
    })


def business_edit_event(request, event_id):
    business = get_current_business(request)
    if business is None:
        return HttpResponse("No business account found", status=404)

    event = Event.objects.filter(id=event_id, organiser=business).first()
    if event is None:
        return HttpResponse("Event not found", status=404)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            event = form.save(commit=False)
            event.date = timezone.make_aware(datetime.datetime.combine(date, time))
            event.save()

            for photo in request.FILES.getlist('photos'):
                EventPhoto.objects.create(event=event, image=photo)

            return redirect('business_my_events')
    else:
        initial = {
            'date': event.date.date(),
            'time': event.date.time(),
        }
        form = EventForm(instance=event, initial=initial)

    return render(request, 'main/business/edit_event.html', {
        'business': business,
        'event': event,
        'form': form,
    })


