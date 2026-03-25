from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.db.models import Q
from django.db import transaction

from .decorators import *
from .forms import LoginForm, EventForm, RegistrationForm
from .models import Event, Customer, Business
from main.models import EventPhoto, Account, Books, Rates

## NOTE: Look at /decorators.py, can use these to check if user is logged in and allow only logged in user to access view. 
##       This is good for like "create event", "rate business", "book event" etc, 





def discover(request):
    events = Event.objects.all()

    query = request.GET.get("q", "").strip()
    location = request.GET.get("location", "").strip()
    date = request.GET.get("date", "").strip()

    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    if location:
        events = events.filter(
            Q(venue__icontains=location) |
            Q(venueAddress__icontains=location)
        )

    if date:
        events = events.filter(date__date=date)

    events = events.order_by("date")

    return render(request, "main/events/discover.html", {
        "events": events,
    })

def about(request):
    return render(request, "main/static_pages/about.html")

def contact(request):
    return render(request, "main/static_pages/contact.html")

def user_login(request):
    if request.session.get('accountId'):
        return redirect("discover")
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
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

def register_choose(request):
    if request.session.get('accountId'):
        return redirect("discover")
    return render(request, 'main/account/register_choose.html')

def register_user(request, accountType):
    if request.session.get('accountId'):
        return redirect("discover")

    if accountType not in ("customer", "business"):
        return redirect("register_choose")

    if request.method == 'POST':
        form = RegistrationForm(request.POST, accountType=accountType)
        if form.is_valid():
            try:
                with transaction.atomic():
                    account = form.save()
                    username = form.cleaned_data.get('username')

                    if accountType == "business":
                        Business.objects.create(account=account, displayName=username)
                    else:
                        Customer.objects.create(accountId=account, name=username)

                request.session["accountId"] = account.id
                request.session["accountType"] = account.accountType
                request.session["accountEmail"] = account.email

                return redirect('discover')
            except Exception:
                form.add_error('email', 'An account with this email already exists.')
    else:
        form = RegistrationForm(accountType=accountType)

    return render(request, 'main/account/register.html', {'form': form, 'accountType': accountType})


def event_detail(request, event_id):

    event =  get_object_or_404(Event, id=event_id)
    event =  get_object_or_404(Event, id=event_id)
    eventPhotos = EventPhoto.objects.filter(event=event)


    avgRating = event.organiser.avgRating
    reviewCount = event.organiser.reviewCount

    if avgRating is None:
        avgRating = 0

    roundedRating = round(avgRating)
    starDisplay = "★" * roundedRating + "☆" * (5 - roundedRating)


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


    event_has_passed = event.date < timezone.now()
    
    show_rating_component = False
    existing_rating = None

    if request.session.get("accountId") and request.session.get("accountType") == "customer":
        customer = Customer.objects.filter(accountId=request.session.get("accountId")).first()

        if customer:
            has_booked = Books.objects.filter(customerId=customer, eventId=event).exists()
            

            if has_booked and event_has_passed:
                show_rating_component = True

                existing_rate = Rates.objects.filter(
                    customerId=customer,
                    businessId=event.organiser
                ).first()

                if existing_rate:
                    existing_rating = existing_rate.rating

    return render(request, "main/events/detail.html", {
        "event": event,
        "eventPhotos": eventPhotos,
        "daysUntilStart": daysUntilStart,
        "capacityPercent": capacityPercent,
        "avgRating": avgRating,
        "reviewCount": reviewCount,
        "starDisplay": starDisplay,
        "show_rating_component": show_rating_component,
        "existing_rating": existing_rating,
        "event_has_passed": event_has_passed,
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

@business_required
def create_event(request):
    if request.method == "POST":

        form = EventForm(request.POST)

        if form.is_valid():

            business = get_object_or_404(
                Business,
                account=request.session.get("accountId")
            )

            event = form.save(commit=False)
            event.organiser = business
            event.currentCapacity = 0
            event.save()

            for photo in request.FILES.getlist("photos"):
                EventPhoto.objects.create(
                    event=event,
                    image=photo
                )

            messages.success(request, "Event created succesfully")
            return redirect("event_detail", event_id=event.id)

        return render(request, "main/business/create_event.html", {
            "form": form,
            "form_data": request.POST,
        })

    return render(request, "main/business/create_event.html", {
        "form": EventForm(),
        "form_data": {},
    })



@customer_required
def rate_event(request, event_id):

    if request.method != "POST":
        return redirect("event_detail", event_id=event_id)

    event = get_object_or_404(Event, id=event_id)
    customer = get_object_or_404(Customer, accountId=request.session.get("accountId"))

    has_booked = Books.objects.filter(customerId=customer, eventId=event).exists()
    event_has_passed = event.date <= timezone.now()

    if not has_booked or not event_has_passed:
        messages.error(request, "You can only rate events you booked after they have passed")
        return redirect("event_detail", event_id=event_id)

    try:
        rating_value = int(request.POST.get("rating"))
    except (TypeError, ValueError):
        messages.error(request, "Invalid rating")
        return redirect("event_detail", event_id=event_id)

    Rates.objects.update_or_create(
        customerId=customer,
        businessId=event.organiser,
        defaults={"rating": rating_value}
    )

    messages.success(request, "Rating submitted successfully.")
    return redirect("event_detail", event_id=event_id)