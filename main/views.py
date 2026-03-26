from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from django.http import JsonResponse
from .decorators import *
from .forms import LoginForm, EventForm, RegistrationForm
from .models import Event, Customer, Business
from main.models import EventPhoto, Account, Books, Rates
from django.shortcuts import render
from django.db.models import Q

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

    if date != "":
        events = events.filter(date__date=date)

    events = events.order_by("date")

    context = {
        "events": events,
    }

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "main/events/_discover_results.html" , context)

    return render(request, "main/events/discover.html", context)

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
    has_booked = False

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
        "has_booked": has_booked,
    })


@customer_required #Decorator handles checking if user logged in and is customer, if not logged in --> /login, if not customer --> /discover
def book_event(request, event_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request."})

    event = get_object_or_404(Event, id=event_id)
    customer = get_object_or_404(Customer, accountId=request.session.get("accountId"))

    if Books.objects.filter(customerId=customer, eventId=event).exists():

        return JsonResponse({"success" : False, "message": "You already booked this event"})

    if event.currentCapacity >= event.maxCapacity:

        return JsonResponse({"success" : False, "message": "This event is full"})

    try:
        Books.objects.create(customerId=customer, eventId=event)

        event.save()


        capacityPercent = 0
        if event.maxCapacity > 0:
            capacityPercent = int((event.currentCapacity / event.maxCapacity) * 100)

        return JsonResponse({
            "success": True,
            "message": "Booking created successfully.",
            "currentCapacity": event.currentCapacity,
            "maxCapacity": event.maxCapacity,
            "capacityPercent": capacityPercent
        })
    except Exception:
        return JsonResponse({"success": False, "message": "Something went wrong."})

@customer_required
def unbook_event(request, event_id):
    if request.method != "POST":
        return redirect("event_detail", event_id=event_id)

    event = get_object_or_404(Event, id=event_id)
    customer = get_object_or_404(Customer, accountId=request.session.get("accountId"))

    booking = Books.objects.filter(customerId=customer, eventId=event).first()

    if not booking:
        return JsonResponse({
            "success": False,
            "message": "You have not booked this event."
        })

    booking.delete()
    event.refresh_from_db()

    capacityPercent = 0
    if event.maxCapacity > 0:
        capacityPercent = int((event.currentCapacity / event.maxCapacity) * 100)

    return JsonResponse({
        "success": True,
        "action": "unbooked",
        "message": "Your booking has been cancelled.",
        "currentCapacity": event.currentCapacity,
        "maxCapacity": event.maxCapacity,
        "capacityPercent": capacityPercent,
    })
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


@customer_required
def my_bookings(request):
    customer = get_object_or_404(Customer, accountId=request.session.get("accountId"))
    now = timezone.now()

    booked_event_ids = Books.objects.filter(customerId=customer).values_list("eventId_id", flat=True)

    upcoming_events = Event.objects.filter( id__in=booked_event_ids, date__gte=now).order_by("date")

    past_events = Event.objects.filter(id__in=booked_event_ids, date__lt=now).order_by("-date")

    rated_business_ids = Rates.objects.filter( customerId=customer).values_list("businessId_id", flat=True)

    rated_events = Event.objects.filter( id__in=booked_event_ids,date__lt=now,organiser_id__in=rated_business_ids).order_by("-date")

    return render(request, "main/bookings/my_bookings.html", {
        "customer": customer,
        "upcoming_events": upcoming_events,
        "past_events": past_events,
        "rated_events": rated_events,
    })
