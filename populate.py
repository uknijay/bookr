import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookr.settings")
django.setup()

from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.core.files import File
from django.db import connection
from datetime import timedelta

from main.models import Account, Business, Customer, Event, EventPhoto, Books, Rates

# ------------------------------------------------
# Data to be populated

defaultPassword = "Password123!"

businessAccounts = [
    {"email": "yoga@example.com",    "displayName": "Zen Flow Studio"},
    {"email": "cooking@example.com", "displayName": "The Cook Lab"},
    {"email": "music@example.com",   "displayName": "Soundwave Events"},
]

customerAccounts = [
    {"email": "alice@example.com",  "name": "Alice Johnson"},
    {"email": "ben@example.com",    "name": "Ben Clarke"},
    {"email": "sara@example.com",   "name": "Sara Patel"},
    {"email": "james@example.com",  "name": "James Doms"},
]

eventData = [
    {
        "business": "yoga@example.com",
        "title": "Morning Vinyasa Flow",
        "description": "A relaxing morning yoga session for all levels.",
        "maxCapacity": 20,
        "venue": "Zen Flow Studio",
        "venueAddress": "239 Byres Rd, Glasgow G12 8UB, United Kingdom",
        "daysFromNow": 7,
    },
    {
        "business": "yoga@example.com",
        "title": "Beginner Pilates",
        "description": "Low-impact full body workout perfect for beginners.",
        "maxCapacity": 15,
        "venue": "Zen Flow Studio",
        "venueAddress": "239 Byres Rd, Glasgow G12 8UB, United Kingdom",
        "daysFromNow": 14,
    },
    {
        "business": "cooking@example.com",
        "title": "Italian Pasta Workshop",
        "description": "Learn to make fresh pasta from scratch with our head chef.",
        "maxCapacity": 10,
        "venue": "The Cook Lab",
        "venueAddress": "73 Berkeley St., Glasgow G3 7DX, United Kingdom",
        "daysFromNow": 10,
    },
    {
        "business": "cooking@example.com",
        "title": "Sourdough Bread Baking",
        "description": "Master the art of sourdough — starter to loaf.",
        "maxCapacity": 8,
        "venue": "The Cook Lab",
        "venueAddress": "73 Berkeley St., Glasgow G3 7DX, United Kingdom",
        "daysFromNow": 21,
    },
    {
        "business": "music@example.com",
        "title": "Live Jazz Night",
        "description": "An evening of live jazz from local artists.",
        "maxCapacity": 50,
        "venue": "The Soundhouse",
        "venueAddress": "43 Ashton Ln, Glasgow G12 8SJ, United Kingdom",
        "daysFromNow": 5,
    },
]

bookingData = [
    ("alice@example.com",  "Morning Vinyasa Flow"),
    ("ben@example.com",    "Morning Vinyasa Flow"),
    ("sara@example.com",   "Italian Pasta Workshop"),
    ("james@example.com",  "Italian Pasta Workshop"),
    ("alice@example.com",  "Live Jazz Night"),
    ("ben@example.com",    "Live Jazz Night"),
    ("sara@example.com",   "Live Jazz Night"),
    ("james@example.com",  "Sourdough Bread Baking"),
]

ratingData = [
    ("alice@example.com",  "yoga@example.com",    5),
    ("ben@example.com",    "yoga@example.com",    4),
    ("sara@example.com",   "cooking@example.com", 5),
    ("james@example.com",  "cooking@example.com", 3),
    ("alice@example.com",  "music@example.com",   4),
]

sampleImages = [
    "population_Images\image1.png",
    "population_Images\image2.png"
]

# ------------------------------------------------
# Helper function
def loadSampleImage(imagePath):
    f = open(imagePath, "rb")
    return File(f, name=os.path.basename(imagePath))




# ------------------------------------------------
# Populate

def populate():
    # Clear data first:
    Books.objects.all().delete()
    Rates.objects.all().delete()
    EventPhoto.objects.all().delete()
    Event.objects.all().delete()
    Customer.objects.all().delete()
    Business.objects.all().delete()
    Account.objects.all().delete()

    # Clear incrementing ID's
    tables = [
        "main_books",
        "main_rates",
        "main_eventphoto",
        "main_event",
        "main_customer",
        "main_business",
        "main_account",
    ]
    with connection.cursor() as cursor:
        for table in tables:
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';")

    hashedPassword = make_password(defaultPassword)

    businesses = {}
    for b in businessAccounts:
        acc = Account.objects.create(
            email=b["email"], 
            password=hashedPassword, 
            accountType="business"
            )
        
        businesses[b["email"]] = Business.objects.create(account=acc, displayName=b["displayName"])


    customers = {}
    for c in customerAccounts:
        acc = Account.objects.create(
            email=c["email"], 
            password=hashedPassword, 
            accountType="customer"
            )
        
        customers[c["email"]] = Customer.objects.create(accountId=acc, name=c["name"])


    events = {}
    for e in eventData:
        event = Event.objects.create(
            title=e["title"],
            description=e["description"],
            maxCapacity=e["maxCapacity"],
            currentCapacity=0,
            venue=e["venue"],
            venueAddress=e["venueAddress"],
            date=timezone.now() + timedelta(days=e["daysFromNow"]),
            organiser=businesses[e["business"]],
        )

        events[e["title"]] = event

        for i, imagePath in enumerate(sampleImages, start=1):
            photo = EventPhoto(event=event, caption=f"{e['title']} — photo {i}", order=i)
            photo.image.save(os.path.basename(imagePath), loadSampleImage(imagePath), save=True)

    for customerEmail, eventTitle in bookingData:
        booking = Books(customerId=customers[customerEmail], eventId=events[eventTitle])
        booking.save()

    for customerEmail, businessEmail, rating in ratingData:
        Rates.objects.create(
            customerId=customers[customerEmail],
            businessId=businesses[businessEmail],
            rating=rating,
        )


if __name__ == "__main__":
    populate()
