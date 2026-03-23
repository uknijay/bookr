import os
import django
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookr.settings")
django.setup()

from datetime import timedelta
from django.utils import timezone
from django.db import connection
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password

from main.models import Account, Business, Customer, Event, EventPhoto, Books, Rates


# ------------------------------------------------
# Config

DEFAULT_PASSWORD = "Password123!"


# ------------------------------------------------
# Seed data

businessAccounts = [
    {"email": "yoga@example.com", "displayName": "Zen Flow Studio"},
    {"email": "cooking@example.com", "displayName": "The Cook Lab"},
    {"email": "music@example.com", "displayName": "Soundwave Events"},
    {"email": "wellness@example.com", "displayName": "Reset Collective"},
    {"email": "tech@example.com", "displayName": "Byte & Build"},
    {"email": "arts@example.com", "displayName": "Canvas Corner"},
]

customerAccounts = [
    {"email": "alice@example.com", "name": "Alice Johnson"},
    {"email": "ben@example.com", "name": "Ben Clarke"},
    {"email": "sara@example.com", "name": "Sara Patel"},
    {"email": "james@example.com", "name": "James Doms"},
    {"email": "mia@example.com", "name": "Mia Roberts"},
    {"email": "noah@example.com", "name": "Noah Campbell"},
    {"email": "zara@example.com", "name": "Zara Ahmed"},
    {"email": "leo@example.com", "name": "Leo Murphy"},
    {"email": "ava@example.com", "name": "Ava Singh"},
    {"email": "ethan@example.com", "name": "Ethan Walker"},
    {"email": "chloe@example.com", "name": "Chloe Martin"},
    {"email": "daniel@example.com", "name": "Daniel Scott"},
]

eventData = [
    {
        "business": "yoga@example.com",
        "title": "Morning Vinyasa Flow",
        "description": "Start the morning with a guided vinyasa yoga class designed to wake up the body and settle the mind. This session combines breathwork, flowing movement, and gentle stretching, making it ideal for anyone looking to improve flexibility, balance, and focus in a calm and welcoming environment.",
        "maxCapacity": 20,
        "venue": "Zen Flow Studio",
        "venueAddress": "239 Byres Rd, Glasgow G12 8UB, United Kingdom",
        "daysFromNow": 4,
        "imageStart": 22,
        "imageCount": 3,
    },
    {
        "business": "yoga@example.com",
        "title": "Sunset Stretch & Breathwork",
        "description": "An evening wellness session built around deep stretching, controlled breathing, and mindful relaxation. Perfect for people who want to release tension after a long day, this class focuses on recovery, posture, and leaving with a genuine sense of calm and reset.",
        "maxCapacity": 18,
        "venue": "Zen Flow Studio",
        "venueAddress": "239 Byres Rd, Glasgow G12 8UB, United Kingdom",
        "daysFromNow": 8,
        "imageStart": 40,
        "imageCount": 2,
    },
    {
        "business": "yoga@example.com",
        "title": "Weekend Mobility Reset",
        "description": "A mobility-focused class aimed at improving joint movement, posture, and overall body control. The session blends yoga-inspired movement with guided mobility drills, making it especially useful for people who sit a lot, train regularly, or simply want to move more freely.",
        "maxCapacity": 16,
        "venue": "Zen Flow Studio",
        "venueAddress": "239 Byres Rd, Glasgow G12 8UB, United Kingdom",
        "daysFromNow": 15,
        "imageStart": 55,
        "imageCount": 4,
    },
    {
        "business": "cooking@example.com",
        "title": "Italian Pasta Workshop",
        "description": "Learn how to make fresh pasta from scratch in this hands-on cooking workshop led by an experienced chef. You will prepare dough by hand, shape different pasta types, and pair them with simple homemade sauces while picking up practical kitchen techniques you can easily repeat at home.",
        "maxCapacity": 12,
        "venue": "The Cook Lab",
        "venueAddress": "73 Berkeley St, Glasgow G3 7DX, United Kingdom",
        "daysFromNow": 6,
        "imageStart": 105,
        "imageCount": 3,
    },
    {
        "business": "cooking@example.com",
        "title": "Sourdough Bread Masterclass",
        "description": "A detailed workshop for anyone curious about the art of sourdough baking. From caring for a starter to shaping, scoring, and baking the final loaf, this session walks through the full process with clear demonstrations and practical advice for better bread at home.",
        "maxCapacity": 10,
        "venue": "The Cook Lab",
        "venueAddress": "73 Berkeley St, Glasgow G3 7DX, United Kingdom",
        "daysFromNow": 11,
        "imageStart": 122,
        "imageCount": 2,
    },
    {
        "business": "cooking@example.com",
        "title": "Street Food Taco Night",
        "description": "A lively cooking event centred around bold flavours, homemade salsas, and creative taco fillings. Guests will build a range of street-food-inspired dishes while learning how to balance spice, texture, and fresh ingredients for a fun and social evening.",
        "maxCapacity": 24,
        "venue": "The Cook Lab",
        "venueAddress": "73 Berkeley St, Glasgow G3 7DX, United Kingdom",
        "daysFromNow": 16,
        "imageStart": 138,
        "imageCount": 4,
    },
    {
        "business": "cooking@example.com",
        "title": "Plant-Based Comfort Food",
        "description": "Discover how to create rich, satisfying comfort food using entirely plant-based ingredients. This class covers flavour layering, texture, and simple techniques that make vegetarian and vegan cooking feel exciting, filling, and surprisingly easy to recreate.",
        "maxCapacity": 14,
        "venue": "The Cook Lab",
        "venueAddress": "73 Berkeley St, Glasgow G3 7DX, United Kingdom",
        "daysFromNow": 21,
        "imageStart": 154,
        "imageCount": 1,
    },
    {
        "business": "music@example.com",
        "title": "Live Jazz Night",
        "description": "Spend the evening enjoying a live jazz performance from talented local musicians in a warm and intimate venue. Expect a mix of classic standards, improvisation, and contemporary influences, creating a relaxed atmosphere that feels both stylish and welcoming.",
        "maxCapacity": 50,
        "venue": "The Soundhouse",
        "venueAddress": "43 Ashton Ln, Glasgow G12 8SJ, United Kingdom",
        "daysFromNow": 5,
        "imageStart": 180,
        "imageCount": 3,
    },
    {
        "business": "music@example.com",
        "title": "Indie Acoustic Sessions",
        "description": "A stripped-back showcase featuring emerging acoustic artists performing original songs in an intimate setting. This event is ideal for anyone who enjoys discovering new talent, hearing raw live performances, and experiencing music in a more personal and conversational format.",
        "maxCapacity": 40,
        "venue": "The Soundhouse",
        "venueAddress": "43 Ashton Ln, Glasgow G12 8SJ, United Kingdom",
        "daysFromNow": 9,
        "imageStart": 194,
        "imageCount": 2,
    },
    {
        "business": "music@example.com",
        "title": "Vinyl Listening Club",
        "description": "Bring your love of music and join an evening dedicated to spinning records, sharing favourites, and hearing new sounds on a proper sound system. This event is as much about conversation and community as it is about music, making it perfect for serious listeners and casual fans alike.",
        "maxCapacity": 22,
        "venue": "The Soundhouse",
        "venueAddress": "43 Ashton Ln, Glasgow G12 8SJ, United Kingdom",
        "daysFromNow": 19,
        "imageStart": 208,
        "imageCount": 1,
    },
    {
        "business": "music@example.com",
        "title": "Open Mic & Poetry Evening",
        "description": "An open and welcoming night for performers, writers, and audiences who enjoy spoken word, acoustic sets, and creative expression. Whether you are stepping up to the mic or simply soaking in the atmosphere, the evening is designed to feel relaxed, inclusive, and full of personality.",
        "maxCapacity": 45,
        "venue": "The Soundhouse",
        "venueAddress": "43 Ashton Ln, Glasgow G12 8SJ, United Kingdom",
        "daysFromNow": 22,
        "imageStart": 220,
        "imageCount": 4,
    },
    {
        "business": "arts@example.com",
        "title": "Watercolour for Beginners",
        "description": "A gentle introduction to watercolour painting with a focus on colour blending, brush control, and simple composition. This class is designed for complete beginners and anyone wanting a calm creative activity that feels approachable, expressive, and rewarding from the very first session.",
        "maxCapacity": 16,
        "venue": "Canvas Corner",
        "venueAddress": "12 Ruthven Ln, Glasgow G12 9BG, United Kingdom",
        "daysFromNow": 7,
        "imageStart": 260,
        "imageCount": 4,
    },
    {
        "business": "arts@example.com",
        "title": "Pottery Wheel Taster",
        "description": "Try the pottery wheel in a hands-on session where you will learn the basics of centring clay, shaping forms, and understanding how pieces are built. This workshop is messy in the best way and offers a fun introduction to ceramics in a supportive studio setting.",
        "maxCapacity": 8,
        "venue": "Canvas Corner",
        "venueAddress": "12 Ruthven Ln, Glasgow G12 9BG, United Kingdom",
        "daysFromNow": 13,
        "imageStart": 276,
        "imageCount": 3,
    },
    {
        "business": "arts@example.com",
        "title": "Urban Sketch Walk",
        "description": "Explore the city while learning how to capture quick scenes, architecture, and everyday moments in sketch form. Participants will be guided through simple drawing techniques, observation skills, and composition ideas that make on-location sketching fun rather than intimidating.",
        "maxCapacity": 18,
        "venue": "Canvas Corner",
        "venueAddress": "12 Ruthven Ln, Glasgow G12 9BG, United Kingdom",
        "daysFromNow": 17,
        "imageStart": 292,
        "imageCount": 2,
    },
    {
        "business": "arts@example.com",
        "title": "Film Photography Basics",
        "description": "A practical introduction to the world of film photography covering camera types, exposure, loading film, and common mistakes to avoid. The session is aimed at beginners who want a slower, more thoughtful approach to photography and a better understanding of analogue image-making.",
        "maxCapacity": 14,
        "venue": "Canvas Corner",
        "venueAddress": "12 Ruthven Ln, Glasgow G12 9BG, United Kingdom",
        "daysFromNow": 18,
        "imageStart": 304,
        "imageCount": 2,
    },
    {
        "business": "wellness@example.com",
        "title": "Cold Water Confidence Workshop",
        "description": "This workshop combines guided breathwork, mindset coaching, and practical safety advice to help participants build confidence around cold water exposure. The experience is designed to be supportive and educational, making it ideal for curious first-timers as well as returning participants.",
        "maxCapacity": 14,
        "venue": "Reset Collective",
        "venueAddress": "1 Bunhouse Rd, Glasgow G3 8UD, United Kingdom",
        "daysFromNow": 12,
        "imageStart": 340,
        "imageCount": 4,
    },
    {
        "business": "wellness@example.com",
        "title": "Mindful Journaling Circle",
        "description": "A quiet and reflective gathering where participants use guided prompts and calm discussion to explore thoughts, goals, and emotions through writing. The atmosphere is intentionally gentle and low-pressure, making it suitable for both experienced journalers and complete beginners.",
        "maxCapacity": 20,
        "venue": "Reset Collective",
        "venueAddress": "1 Bunhouse Rd, Glasgow G3 8UD, United Kingdom",
        "daysFromNow": 14,
        "imageStart": 356,
        "imageCount": 1,
    },
    {
        "business": "wellness@example.com",
        "title": "Sunday Sound Bath",
        "description": "A restorative session using sound and vibration to create a deeply calming environment for rest and reset. Participants are invited to lie back, slow down, and unwind while surrounded by soothing tones designed to encourage stillness and relaxation.",
        "maxCapacity": 22,
        "venue": "Reset Collective",
        "venueAddress": "1 Bunhouse Rd, Glasgow G3 8UD, United Kingdom",
        "daysFromNow": 20,
        "imageStart": 370,
        "imageCount": 3,
    },
    {
        "business": "tech@example.com",
        "title": "Intro to Python Night",
        "description": "A beginner-friendly coding evening covering the fundamentals of Python through live demonstrations and small interactive exercises. The event is designed to feel approachable and practical, making it a solid starting point for anyone curious about programming or looking to refresh the basics.",
        "maxCapacity": 30,
        "venue": "Byte & Build Hub",
        "venueAddress": "110 Queen St, Glasgow G1 3BX, United Kingdom",
        "daysFromNow": 3,
        "imageStart": 410,
        "imageCount": 3,
    },
    {
        "business": "tech@example.com",
        "title": "Startup Pitch Practice",
        "description": "A collaborative session for founders, builders, and ambitious students who want to sharpen how they present an idea. Attendees will have the opportunity to test their pitch, receive feedback, and hear how others communicate their products, vision, and value clearly.",
        "maxCapacity": 28,
        "venue": "Byte & Build Hub",
        "venueAddress": "110 Queen St, Glasgow G1 3BX, United Kingdom",
        "daysFromNow": 10,
        "imageStart": 424,
        "imageCount": 2,
    },
    {
        "business": "tech@example.com",
        "title": "Robotics Builders Meetup",
        "description": "A meetup for hardware enthusiasts, students, and makers who enjoy building robots and experimenting with physical computing. Expect demos, discussion, project sharing, and plenty of conversation around design choices, components, programming, and hands-on problem solving.",
        "maxCapacity": 25,
        "venue": "Byte & Build Hub",
        "venueAddress": "110 Queen St, Glasgow G1 3BX, United Kingdom",
        "daysFromNow": 15,
        "imageStart": 438,
        "imageCount": 4,
    },
]

bookingData = [
    ("alice@example.com", "Morning Vinyasa Flow"),
    ("ben@example.com", "Morning Vinyasa Flow"),
    ("sara@example.com", "Morning Vinyasa Flow"),
    ("james@example.com", "Sunset Stretch & Breathwork"),
    ("mia@example.com", "Sunset Stretch & Breathwork"),
    ("noah@example.com", "Weekend Mobility Reset"),
    ("zara@example.com", "Italian Pasta Workshop"),
    ("leo@example.com", "Italian Pasta Workshop"),
    ("ava@example.com", "Italian Pasta Workshop"),
    ("ethan@example.com", "Sourdough Bread Masterclass"),
    ("chloe@example.com", "Street Food Taco Night"),
    ("daniel@example.com", "Street Food Taco Night"),
    ("alice@example.com", "Street Food Taco Night"),
    ("ben@example.com", "Plant-Based Comfort Food"),
    ("mia@example.com", "Live Jazz Night"),
    ("noah@example.com", "Live Jazz Night"),
    ("zara@example.com", "Live Jazz Night"),
    ("leo@example.com", "Indie Acoustic Sessions"),
    ("ava@example.com", "Vinyl Listening Club"),
    ("ethan@example.com", "Open Mic & Poetry Evening"),
    ("chloe@example.com", "Open Mic & Poetry Evening"),
    ("daniel@example.com", "Watercolour for Beginners"),
    ("alice@example.com", "Watercolour for Beginners"),
    ("james@example.com", "Pottery Wheel Taster"),
    ("mia@example.com", "Urban Sketch Walk"),
    ("sara@example.com", "Film Photography Basics"),
    ("ben@example.com", "Cold Water Confidence Workshop"),
    ("zara@example.com", "Mindful Journaling Circle"),
    ("leo@example.com", "Sunday Sound Bath"),
    ("ava@example.com", "Intro to Python Night"),
    ("ethan@example.com", "Intro to Python Night"),
    ("chloe@example.com", "Startup Pitch Practice"),
    ("daniel@example.com", "Robotics Builders Meetup"),
    ("noah@example.com", "Robotics Builders Meetup"),
]

ratingData = [
    ("alice@example.com", "yoga@example.com", 5),
    ("ben@example.com", "yoga@example.com", 4),
    ("sara@example.com", "cooking@example.com", 5),
    ("james@example.com", "cooking@example.com", 4),
    ("mia@example.com", "music@example.com", 5),
    ("noah@example.com", "music@example.com", 4),
    ("zara@example.com", "arts@example.com", 5),
    ("leo@example.com", "arts@example.com", 4),
    ("ava@example.com", "wellness@example.com", 5),
    ("ethan@example.com", "wellness@example.com", 4),
    ("chloe@example.com", "tech@example.com", 5),
    ("daniel@example.com", "tech@example.com", 4),
]


# ------------------------------------------------
# Helpers

def makeOnlineImageUrls(startIndex, count):
    urls = []
    for i in range(count):
        imageNumber = startIndex + i
        urls.append(f"https://yavuzceliker.github.io/sample-images/image-{imageNumber}.jpg")
    return urls


def downloadImageAsContentFile(url, filename):
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return ContentFile(response.content, name=filename)


# ------------------------------------------------
# Populate

def populate():
    print("Clearing existing data...")

    Books.objects.all().delete()
    Rates.objects.all().delete()
    EventPhoto.objects.all().delete()
    Event.objects.all().delete()
    Customer.objects.all().delete()
    Business.objects.all().delete()
    Account.objects.all().delete()

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
            try:
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';")
            except Exception:
                pass

    hashedPassword = make_password(DEFAULT_PASSWORD)

    print("Creating businesses...")
    businesses = {}
    for businessData in businessAccounts:
        account = Account.objects.create(
            email=businessData["email"],
            password=hashedPassword,
            accountType="business",
        )
        business = Business.objects.create(
            account=account,
            displayName=businessData["displayName"],
        )
        businesses[businessData["email"]] = business

    print("Creating customers...")
    customers = {}
    for customerData in customerAccounts:
        account = Account.objects.create(
            email=customerData["email"],
            password=hashedPassword,
            accountType="customer",
        )
        customer = Customer.objects.create(
            accountId=account,
            name=customerData["name"],
        )
        customers[customerData["email"]] = customer

    print("Creating events and downloading images...")
    events = {}

    for eventInfo in eventData:
        event = Event.objects.create(
            title=eventInfo["title"],
            description=eventInfo["description"],
            maxCapacity=eventInfo["maxCapacity"],
            currentCapacity=0,
            venue=eventInfo["venue"],
            venueAddress=eventInfo["venueAddress"],
            date=timezone.now() + timedelta(days=eventInfo["daysFromNow"]),
            organiser=businesses[eventInfo["business"]],
        )

        imageUrls = makeOnlineImageUrls(
            startIndex=eventInfo["imageStart"],
            count=eventInfo["imageCount"],
        )

        for order, imageUrl in enumerate(imageUrls, start=1):
            safeTitle = event.title.lower().replace(" ", "_").replace("&", "and")
            filename = f"{safeTitle}_{order}.jpg"

            try:
                imageFile = downloadImageAsContentFile(imageUrl, filename)
                photo = EventPhoto(
                    event=event,
                    caption=f"{event.title} — photo {order}",
                    order=order,
                )
                photo.image.save(filename, imageFile, save=True)
                print(f"  Added image {order} for {event.title}")
            except Exception as exc:
                print(f"  Could not download image for '{event.title}' from {imageUrl}: {exc}")

        events[eventInfo["title"]] = event

    print("Creating bookings...")
    bookingsPerEvent = {}

    for customerEmail, eventTitle in bookingData:
        Books.objects.create(
            customerId=customers[customerEmail],
            eventId=events[eventTitle],
        )
        bookingsPerEvent[eventTitle] = bookingsPerEvent.get(eventTitle, 0) + 1

    for eventTitle, count in bookingsPerEvent.items():
        event = events[eventTitle]
        event.currentCapacity = count
        event.save(update_fields=["currentCapacity"])

    print("Creating ratings...")
    for customerEmail, businessEmail, rating in ratingData:
        Rates.objects.create(
            customerId=customers[customerEmail],
            businessId=businesses[businessEmail],
            rating=rating,
        )

    print("Done.")
    print(f"Businesses created: {len(businessAccounts)}")
    print(f"Customers created: {len(customerAccounts)}")
    print(f"Events created: {len(eventData)}")
    print(f"Bookings created: {len(bookingData)}")
    print(f"Ratings created: {len(ratingData)}")


if __name__ == "__main__":
    populate()