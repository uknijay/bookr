
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookr.settings")
django.setup()
import requests
from django.core.files.base import ContentFile
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
    {"email": "wellness@example.com", "displayName": "West Wellness Hub"},
    {"email": "art@example.com",      "displayName": "Canvas & Co"},
    {"email": "comedy@example.com",   "displayName": "Laugh Loft"},
    {"email": "fitness@example.com",  "displayName": "Pulse Studio"},
    {"email": "network@example.com",  "displayName": "City Connect Events"},
    {"email": "food@example.com",     "displayName": "Merchant Food Rooms"},
    {"email": "culture@example.com",  "displayName": "Gather Glasgow"},
]

customerAccounts = [
    {"email": "alice@example.com",   "name": "Alice Johnson"},
    {"email": "ben@example.com",     "name": "Ben Clarke"},
    {"email": "sara@example.com",    "name": "Sara Patel"},
    {"email": "james@example.com",   "name": "James Doms"},
    {"email": "lisa@example.com",    "name": "Lisa Thompson"},
    {"email": "michael@example.com", "name": "Michael Brown"},
    {"email": "emma@example.com",    "name": "Emma Wilson"},
    {"email": "daniel@example.com",  "name": "Daniel Evans"},
    {"email": "olivia@example.com",  "name": "Olivia Harris"},
    {"email": "noah@example.com",    "name": "Noah Walker"},
    {"email": "ava@example.com",     "name": "Ava Robinson"},
    {"email": "liam@example.com",    "name": "Liam Hall"},
    {"email": "mia@example.com",     "name": "Mia Allen"},
    {"email": "ethan@example.com",   "name": "Ethan Young"},
    {"email": "grace@example.com",   "name": "Grace King"},
    {"email": "lucas@example.com",   "name": "Lucas Wright"},
    {"email": "chloe@example.com",   "name": "Chloe Scott"},
    {"email": "jack@example.com",    "name": "Jack Green"},
    {"email": "ella@example.com",    "name": "Ella Adams"},
    {"email": "henry@example.com",   "name": "Henry Baker"},
    {"email": "sophie@example.com",  "name": "Sophie Nelson"},
    {"email": "oscar@example.com",   "name": "Oscar Carter"},
    {"email": "lily@example.com",    "name": "Lily Mitchell"},
    {"email": "charlie@example.com", "name": "Charlie Perez"},
    {"email": "isla@example.com",    "name": "Isla Roberts"},
    {"email": "leo@example.com",     "name": "Leo Turner"},
    {"email": "zoe@example.com",     "name": "Zoe Phillips"},
    {"email": "freddie@example.com", "name": "Freddie Campbell"},
    {"email": "ruby@example.com",    "name": "Ruby Parker"},
    {"email": "theo@example.com",    "name": "Theo Edwards"},
    {"email": "evie@example.com",    "name": "Evie Collins"},
    {"email": "arthur@example.com",  "name": "Arthur Stewart"},
    {"email": "poppy@example.com",   "name": "Poppy Sanchez"},
    {"email": "archie@example.com",  "name": "Archie Morris"},
    {"email": "ivy@example.com",     "name": "Ivy Rogers"},
    {"email": "george@example.com",  "name": "George Reed"},
    {"email": "rosie@example.com",   "name": "Rosie Cook"},
    {"email": "harry@example.com",   "name": "Harry Morgan"},
    {"email": "daisy@example.com",   "name": "Daisy Bell"},
    {"email": "max@example.com",     "name": "Max Murphy"},
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
        "description": "A low-impact full body workout designed for beginners.",
        "maxCapacity": 15,
        "venue": "Zen Flow Studio",
        "venueAddress": "239 Byres Rd, Glasgow G12 8UB, United Kingdom",
        "daysFromNow": 14,
    },
    {
        "business": "yoga@example.com",
        "title": "Evening Mindfulness Yoga",
        "description": "A calming evening yoga session focused on breathing, stretching, and relaxation.",
        "maxCapacity": 18,
        "venue": "Zen Flow Studio",
        "venueAddress": "239 Byres Rd, Glasgow G12 8UB, United Kingdom",
        "daysFromNow": 24,
    },

    {
        "business": "cooking@example.com",
        "title": "Italian Pasta Workshop",
        "description": "Learn to make fresh pasta from scratch with guidance from our head chef.",
        "maxCapacity": 15,
        "venue": "The Cook Lab",
        "venueAddress": "73 Berkeley St., Glasgow G3 7DX, United Kingdom",
        "daysFromNow": 10,
    },
    {
        "business": "cooking@example.com",
        "title": "Sourdough Bread Baking",
        "description": "Master the art of sourdough, from starter preparation to the final loaf.",
        "maxCapacity": 8,
        "venue": "The Cook Lab",
        "venueAddress": "73 Berkeley St., Glasgow G3 7DX, United Kingdom",
        "daysFromNow": 21,
    },
    {
        "business": "cooking@example.com",
        "title": "Street Food Masterclass",
        "description": "Learn to create bold, vibrant street food dishes inspired by global flavours.",
        "maxCapacity": 14,
        "venue": "The Cook Lab",
        "venueAddress": "73 Berkeley St., Glasgow G3 7DX, United Kingdom",
        "daysFromNow": 30,
    },

    {
        "business": "music@example.com",
        "title": "Live Jazz Night",
        "description": "An evening of live jazz performances from talented local artists.",
        "maxCapacity": 50,
        "venue": "The Soundhouse",
        "venueAddress": "43 Ashton Ln, Glasgow G12 8SJ, United Kingdom",
        "daysFromNow": 5,
    },
    {
        "business": "music@example.com",
        "title": "Acoustic Sessions Live",
        "description": "A laid-back live music night featuring acoustic performances and local talent.",
        "maxCapacity": 40,
        "venue": "The Soundhouse",
        "venueAddress": "43 Ashton Ln, Glasgow G12 8SJ, United Kingdom",
        "daysFromNow": 17,
    },
    {
        "business": "music@example.com",
        "title": "Friday DJ Showcase",
        "description": "A high-energy night of DJ sets featuring house, dance, and electronic music.",
        "maxCapacity": 90,
        "venue": "The Soundhouse",
        "venueAddress": "43 Ashton Ln, Glasgow G12 8SJ, United Kingdom",
        "daysFromNow": 28,
    },

    {
        "business": "wellness@example.com",
        "title": "Breathwork for Beginners",
        "description": "An introductory breathwork session designed to improve calm, focus, and wellbeing.",
        "maxCapacity": 20,
        "venue": "West Wellness Hub",
        "venueAddress": "55 Dumbarton Rd, Glasgow G11 6PW, United Kingdom",
        "daysFromNow": 8,
    },
    {
        "business": "wellness@example.com",
        "title": "Mobility & Recovery Workshop",
        "description": "A guided mobility session focused on flexibility, recovery, and movement quality.",
        "maxCapacity": 22,
        "venue": "West Wellness Hub",
        "venueAddress": "55 Dumbarton Rd, Glasgow G11 6PW, United Kingdom",
        "daysFromNow": 19,
    },
    {
        "business": "wellness@example.com",
        "title": "Weekend Reset Circle",
        "description": "A restorative wellness session with light movement, mindfulness, and reflection.",
        "maxCapacity": 18,
        "venue": "West Wellness Hub",
        "venueAddress": "55 Dumbarton Rd, Glasgow G11 6PW, United Kingdom",
        "daysFromNow": 33,
    },

    {
        "business": "art@example.com",
        "title": "Watercolour for Starters",
        "description": "A beginner-friendly art workshop exploring watercolour techniques and colour blending.",
        "maxCapacity": 12,
        "venue": "Canvas & Co",
        "venueAddress": "18 Hillhead St, Glasgow G12 8QE, United Kingdom",
        "daysFromNow": 9,
    },
    {
        "business": "art@example.com",
        "title": "Urban Sketching Evening",
        "description": "A relaxed sketching workshop focused on architecture, perspective, and observation.",
        "maxCapacity": 15,
        "venue": "Canvas & Co",
        "venueAddress": "18 Hillhead St, Glasgow G12 8QE, United Kingdom",
        "daysFromNow": 22,
    },
    {
        "business": "art@example.com",
        "title": "Creative Collage Workshop",
        "description": "A hands-on mixed media session where participants create expressive collage pieces.",
        "maxCapacity": 14,
        "venue": "Canvas & Co",
        "venueAddress": "18 Hillhead St, Glasgow G12 8QE, United Kingdom",
        "daysFromNow": 36,
    },

    {
        "business": "comedy@example.com",
        "title": "Open Mic Comedy Night",
        "description": "A local comedy night featuring fresh acts, short sets, and a lively audience.",
        "maxCapacity": 55,
        "venue": "Laugh Loft",
        "venueAddress": "27 Renfield Lane, Glasgow G2 5AR, United Kingdom",
        "daysFromNow": 7,
    },
    {
        "business": "comedy@example.com",
        "title": "Stand-Up Showcase",
        "description": "An evening of stand-up comedy from a mix of emerging and established performers.",
        "maxCapacity": 70,
        "venue": "Laugh Loft",
        "venueAddress": "27 Renfield Lane, Glasgow G2 5AR, United Kingdom",
        "daysFromNow": 18,
    },
    {
        "business": "comedy@example.com",
        "title": "Late Night Laughs",
        "description": "A weekend comedy special packed with quick sets and crowd interaction.",
        "maxCapacity": 65,
        "venue": "Laugh Loft",
        "venueAddress": "27 Renfield Lane, Glasgow G2 5AR, United Kingdom",
        "daysFromNow": 31,
    },

    {
        "business": "fitness@example.com",
        "title": "HIIT Fundamentals",
        "description": "An introduction to high-intensity interval training with beginner-friendly options.",
        "maxCapacity": 24,
        "venue": "Pulse Studio",
        "venueAddress": "88 Argyle St, Glasgow G2 8BG, United Kingdom",
        "daysFromNow": 10,
    },
    {
        "business": "fitness@example.com",
        "title": "Core Strength Express",
        "description": "A focused workout session designed to improve abdominal strength and stability.",
        "maxCapacity": 20,
        "venue": "Pulse Studio",
        "venueAddress": "88 Argyle St, Glasgow G2 8BG, United Kingdom",
        "daysFromNow": 20,
    },
    {
        "business": "fitness@example.com",
        "title": "Weekend Conditioning Session",
        "description": "A full-body conditioning workout to build endurance and movement confidence.",
        "maxCapacity": 26,
        "venue": "Pulse Studio",
        "venueAddress": "88 Argyle St, Glasgow G2 8BG, United Kingdom",
        "daysFromNow": 34,
    },

    {
        "business": "network@example.com",
        "title": "Startup Networking Mixer",
        "description": "A social event for founders, developers, and creatives to connect and share ideas.",
        "maxCapacity": 60,
        "venue": "City Connect Events",
        "venueAddress": "110 Queen St, Glasgow G1 3BX, United Kingdom",
        "daysFromNow": 12,
    },
    {
        "business": "network@example.com",
        "title": "Young Professionals Meetup",
        "description": "A networking evening for students, graduates, and early-career professionals.",
        "maxCapacity": 50,
        "venue": "City Connect Events",
        "venueAddress": "110 Queen St, Glasgow G1 3BX, United Kingdom",
        "daysFromNow": 23,
    },
    {
        "business": "network@example.com",
        "title": "Tech & Business Social",
        "description": "A relaxed crossover event bringing together tech-minded people and business owners.",
        "maxCapacity": 70,
        "venue": "City Connect Events",
        "venueAddress": "110 Queen St, Glasgow G1 3BX, United Kingdom",
        "daysFromNow": 37,
    },

    {
        "business": "food@example.com",
        "title": "Brunch Classics Workshop",
        "description": "Learn how to prepare and plate a range of popular brunch favourites.",
        "maxCapacity": 16,
        "venue": "Merchant Food Rooms",
        "venueAddress": "24 Candleriggs, Glasgow G1 1LD, United Kingdom",
        "daysFromNow": 11,
    },
    {
        "business": "food@example.com",
        "title": "Seasonal Small Plates",
        "description": "A cooking session focused on fresh ingredients and elegant seasonal dishes.",
        "maxCapacity": 14,
        "venue": "Merchant Food Rooms",
        "venueAddress": "24 Candleriggs, Glasgow G1 1LD, United Kingdom",
        "daysFromNow": 24,
    },
    {
        "business": "food@example.com",
        "title": "Dessert Plating Essentials",
        "description": "A practical workshop on preparing and presenting restaurant-style desserts.",
        "maxCapacity": 10,
        "venue": "Merchant Food Rooms",
        "venueAddress": "24 Candleriggs, Glasgow G1 1LD, United Kingdom",
        "daysFromNow": 38,
    },

    {
        "business": "culture@example.com",
        "title": "Local Culture Evening",
        "description": "A community event celebrating stories, music, and creative voices from Glasgow.",
        "maxCapacity": 80,
        "venue": "Gather Glasgow",
        "venueAddress": "60 Trongate, Glasgow G1 5EP, United Kingdom",
        "daysFromNow": 15,
    },
    {
        "business": "culture@example.com",
        "title": "Spoken Word & Stories",
        "description": "A welcoming spoken word evening featuring local performers and guests.",
        "maxCapacity": 45,
        "venue": "Gather Glasgow",
        "venueAddress": "60 Trongate, Glasgow G1 5EP, United Kingdom",
        "daysFromNow": 27,
    },
    {
        "business": "culture@example.com",
        "title": "Creative Community Gathering",
        "description": "A social event bringing together artists, writers, and community organisers.",
        "maxCapacity": 65,
        "venue": "Gather Glasgow",
        "venueAddress": "60 Trongate, Glasgow G1 5EP, United Kingdom",
        "daysFromNow": 41,
    },
        {
        "business": "yoga@example.com",
        "title": "Spring Reset Yoga",
        "description": "A restorative yoga session focused on gentle movement, stretching, and relaxation.",
        "maxCapacity": 18,
        "venue": "Zen Flow Studio",
        "venueAddress": "239 Byres Rd, Glasgow G12 8UB, United Kingdom",
        "daysFromNow": -7,
    },
    {
        "business": "cooking@example.com",
        "title": "Fresh Ravioli Workshop",
        "description": "A hands-on pasta session where participants learned to make and fill fresh ravioli from scratch.",
        "maxCapacity": 15,
        "venue": "The Cook Lab",
        "venueAddress": "73 Berkeley St., Glasgow G3 7DX, United Kingdom",
        "daysFromNow": -12,
    },
    {
        "business": "music@example.com",
        "title": "Soul & Jazz Evening",
        "description": "A live music event featuring a mix of soul vocals and jazz instrumentals from local performers.",
        "maxCapacity": 50,
        "venue": "The Soundhouse",
        "venueAddress": "43 Ashton Ln, Glasgow G12 8SJ, United Kingdom",
        "daysFromNow": -5,
    },
    {
        "business": "wellness@example.com",
        "title": "Midweek Recovery Session",
        "description": "A guided wellness class centred on breathing, light stretching, and physical recovery.",
        "maxCapacity": 20,
        "venue": "West Wellness Hub",
        "venueAddress": "55 Dumbarton Rd, Glasgow G11 6PW, United Kingdom",
        "daysFromNow": -9,
    },
    {
        "business": "art@example.com",
        "title": "Acrylic Painting Night",
        "description": "An evening workshop exploring acrylic painting techniques, layering, and colour mixing.",
        "maxCapacity": 14,
        "venue": "Canvas & Co",
        "venueAddress": "18 Hillhead St, Glasgow G12 8QE, United Kingdom",
        "daysFromNow": -15,
    },
    {
        "business": "comedy@example.com",
        "title": "Saturday Stand-Up Spotlight",
        "description": "A comedy showcase featuring short sets from emerging comedians and returning favourites.",
        "maxCapacity": 65,
        "venue": "Laugh Loft",
        "venueAddress": "27 Renfield Lane, Glasgow G2 5AR, United Kingdom",
        "daysFromNow": -6,
    },
    {
        "business": "food@example.com",
        "title": "Small Plates Kitchen Session",
        "description": "A practical cooking workshop focused on preparing elegant sharing plates with seasonal ingredients.",
        "maxCapacity": 12,
        "venue": "Merchant Food Rooms",
        "venueAddress": "24 Candleriggs, Glasgow G1 1LD, United Kingdom",
        "daysFromNow": -11,
    },
    {
        "business": "culture@example.com",
        "title": "Community Poetry Night",
        "description": "A relaxed spoken word evening with local poets, stories, and open community participation.",
        "maxCapacity": 40,
        "venue": "Gather Glasgow",
        "venueAddress": "60 Trongate, Glasgow G1 5EP, United Kingdom",
        "daysFromNow": -14,
    },
]

bookingData = [

    ("ben@example.com", "Startup Networking Mixer"),
    ("ben@example.com", "Morning Vinyasa Flow"),
    ("ben@example.com", "Brunch Classics Workshop"),

    ("ben@example.com", "Spring Reset Yoga"),
    ("ben@example.com", "Fresh Ravioli Workshop"),
    ("ben@example.com", "Soul & Jazz Evening"),
    ("ben@example.com", "Community Poetry Night"),

    ("sara@example.com",    "Italian Pasta Workshop"),
    ("sara@example.com",    "Live Jazz Night"),

    ("james@example.com",   "Italian Pasta Workshop"),
    ("james@example.com",   "Startup Networking Mixer"),

    ("lisa@example.com",    "Italian Pasta Workshop"),
    ("lisa@example.com",    "Live Jazz Night"),

    ("michael@example.com", "Italian Pasta Workshop"),
    ("michael@example.com", "Startup Networking Mixer"),

    ("emma@example.com",    "Italian Pasta Workshop"),
    ("emma@example.com",    "Live Jazz Night"),

    ("daniel@example.com",  "Italian Pasta Workshop"),
    ("daniel@example.com",  "Startup Networking Mixer"),

    ("olivia@example.com",  "Italian Pasta Workshop"),
    ("olivia@example.com",  "Live Jazz Night"),

    ("noah@example.com",    "Italian Pasta Workshop"),
    ("noah@example.com",    "Startup Networking Mixer"),

    ("ava@example.com",     "Live Jazz Night"),
    ("ava@example.com",     "Morning Vinyasa Flow"),

    ("liam@example.com",    "Live Jazz Night"),
    ("liam@example.com",    "Beginner Pilates"),

    ("mia@example.com",     "Live Jazz Night"),
    ("mia@example.com",     "Breathwork for Beginners"),

    ("ethan@example.com",   "Live Jazz Night"),
    ("ethan@example.com",   "Watercolour for Starters"),

    ("grace@example.com",   "Live Jazz Night"),
    ("grace@example.com",   "Open Mic Comedy Night"),

    ("lucas@example.com",   "Live Jazz Night"),
    ("lucas@example.com",   "HIIT Fundamentals"),

    ("chloe@example.com",   "Live Jazz Night"),
    ("chloe@example.com",   "Brunch Classics Workshop"),

    ("jack@example.com",    "Live Jazz Night"),
    ("jack@example.com",    "Local Culture Evening"),

    ("ella@example.com",    "Live Jazz Night"),
    ("ella@example.com",    "Acoustic Sessions Live"),

    ("henry@example.com",   "Startup Networking Mixer"),
    ("henry@example.com",   "Young Professionals Meetup"),

    ("sophie@example.com",  "Startup Networking Mixer"),
    ("sophie@example.com",  "Tech & Business Social"),

    ("oscar@example.com",   "Startup Networking Mixer"),
    ("oscar@example.com",   "Friday DJ Showcase"),

    ("lily@example.com",    "Startup Networking Mixer"),
    ("lily@example.com",    "Weekend Reset Circle"),

    ("charlie@example.com", "Startup Networking Mixer"),
    ("charlie@example.com", "Urban Sketching Evening"),

    ("isla@example.com",    "Startup Networking Mixer"),
    ("isla@example.com",    "Stand-Up Showcase"),

    ("leo@example.com",     "Startup Networking Mixer"),
    ("leo@example.com",     "Core Strength Express"),

    ("zoe@example.com",     "Startup Networking Mixer"),
    ("zoe@example.com",     "Seasonal Small Plates"),

    ("freddie@example.com", "Startup Networking Mixer"),
    ("freddie@example.com", "Spoken Word & Stories"),

    ("ruby@example.com",    "Startup Networking Mixer"),
    ("ruby@example.com",    "Creative Community Gathering"),

    ("theo@example.com",    "Morning Vinyasa Flow"),
    ("theo@example.com",    "Soul & Jazz Evening"),

    ("evie@example.com",    "Beginner Pilates"),
    ("evie@example.com",    "Fresh Ravioli Workshop"),

    ("arthur@example.com",  "Evening Mindfulness Yoga"),
    ("arthur@example.com",  "Mobility & Recovery Workshop"),

    ("poppy@example.com",   "Street Food Masterclass"),
    ("poppy@example.com",   "Acrylic Painting Night"),

    ("archie@example.com",  "Saturday Stand-Up Spotlight"),
    ("archie@example.com",  "HIIT Fundamentals"),

    ("ivy@example.com",     "Core Strength Express"),
    ("ivy@example.com",     "Community Poetry Night"),

    ("george@example.com",  "Brunch Classics Workshop"),
    ("george@example.com",  "Local Culture Evening"),

    ("rosie@example.com",   "Dessert Plating Essentials"),
    ("rosie@example.com",   "Spoken Word & Stories"),

    ("harry@example.com",   "Spring Reset Yoga"),
    ("harry@example.com",   "Midweek Recovery Session"),

    ("daisy@example.com",   "Small Plates Kitchen Session"),
    ("daisy@example.com",   "Creative Collage Workshop"),

    ("max@example.com",     "Late Night Laughs"),
    ("max@example.com",     "Weekend Conditioning Session"),
]

ratingData = [
    ("alice@example.com",   "yoga@example.com",     5),
    ("alice@example.com",   "music@example.com",    4),
    ("alice@example.com",   "food@example.com",     5),

    ("ben@example.com", "yoga@example.com", 4),
    ("ben@example.com", "cooking@example.com", 5),
    ("ben@example.com", "music@example.com", 4),

    ("sara@example.com",    "cooking@example.com",  5),
    ("sara@example.com",    "music@example.com",    4),
    ("sara@example.com",    "food@example.com",     4),

    ("james@example.com",   "cooking@example.com",  3),
    ("james@example.com",   "network@example.com",  4),
    ("james@example.com",   "comedy@example.com",   4),

    ("lisa@example.com",    "cooking@example.com",  5),
    ("lisa@example.com",    "music@example.com",    5),
    ("lisa@example.com",    "art@example.com",      4),

    ("michael@example.com", "cooking@example.com",  4),
    ("michael@example.com", "network@example.com",  5),
    ("michael@example.com", "fitness@example.com",  4),

    ("emma@example.com",    "cooking@example.com",  5),
    ("emma@example.com",    "music@example.com",    4),
    ("emma@example.com",    "culture@example.com",  5),

    ("daniel@example.com",  "cooking@example.com",  4),
    ("daniel@example.com",  "network@example.com",  4),
    ("daniel@example.com",  "comedy@example.com",   3),

    ("olivia@example.com",  "cooking@example.com",  5),
    ("olivia@example.com",  "music@example.com",    5),
    ("olivia@example.com",  "yoga@example.com",     4),

    ("noah@example.com",    "cooking@example.com",  4),
    ("noah@example.com",    "network@example.com",  5),
    ("noah@example.com",    "fitness@example.com",  4),

    ("ava@example.com",     "music@example.com",    5),
    ("ava@example.com",     "yoga@example.com",     4),
    ("ava@example.com",     "wellness@example.com", 5),

    ("liam@example.com",    "music@example.com",    4),
    ("liam@example.com",    "yoga@example.com",     4),
    ("liam@example.com",    "fitness@example.com",  3),

    ("mia@example.com",     "music@example.com",    5),
    ("mia@example.com",     "wellness@example.com", 4),
    ("mia@example.com",     "fitness@example.com",  4),

    ("ethan@example.com",   "music@example.com",    4),
    ("ethan@example.com",   "art@example.com",      5),
    ("ethan@example.com",   "food@example.com",     4),

    ("grace@example.com",   "music@example.com",    5),
    ("grace@example.com",   "comedy@example.com",   5),
    ("grace@example.com",   "culture@example.com",  4),

    ("lucas@example.com",   "music@example.com",    4),
    ("lucas@example.com",   "fitness@example.com",  5),
    ("lucas@example.com",   "network@example.com",  4),

    ("chloe@example.com",   "music@example.com",    4),
    ("chloe@example.com",   "food@example.com",     5),
    ("chloe@example.com",   "culture@example.com",  4),

    ("jack@example.com",    "music@example.com",    5),
    ("jack@example.com",    "culture@example.com",  5),
    ("jack@example.com",    "network@example.com",  4),

    ("ella@example.com",    "music@example.com",    4),
    ("ella@example.com",    "culture@example.com",  4),
    ("ella@example.com",    "art@example.com",      5),

    ("henry@example.com",   "network@example.com",  5),
    ("henry@example.com",   "music@example.com",    4),
    ("henry@example.com",   "culture@example.com",  4),

    ("sophie@example.com",  "network@example.com",  5),
    ("sophie@example.com",  "comedy@example.com",   4),
    ("sophie@example.com",  "fitness@example.com",  4),

    ("oscar@example.com",   "network@example.com",  4),
    ("oscar@example.com",   "music@example.com",    5),
    ("oscar@example.com",   "comedy@example.com",   4),

    ("lily@example.com",    "network@example.com",  5),
    ("lily@example.com",    "wellness@example.com", 5),
    ("lily@example.com",    "yoga@example.com",     4),

    ("charlie@example.com", "network@example.com",  4),
    ("charlie@example.com", "art@example.com",      5),
    ("charlie@example.com", "culture@example.com",  4),

    ("isla@example.com",    "network@example.com",  5),
    ("isla@example.com",    "comedy@example.com",   5),
    ("isla@example.com",    "food@example.com",     4),

    ("leo@example.com",     "network@example.com",  4),
    ("leo@example.com",     "fitness@example.com",  5),
    ("leo@example.com",     "wellness@example.com", 4),

    ("zoe@example.com",     "network@example.com",  5),
    ("zoe@example.com",     "food@example.com",     5),
    ("zoe@example.com",     "cooking@example.com",  4),

    ("freddie@example.com", "network@example.com",  4),
    ("freddie@example.com", "culture@example.com",  5),
    ("freddie@example.com", "music@example.com",    4),

    ("ruby@example.com",    "network@example.com",  5),
    ("ruby@example.com",    "culture@example.com",  5),
    ("ruby@example.com",    "art@example.com",      4),

    ("theo@example.com",    "music@example.com",    5),
    ("theo@example.com",    "yoga@example.com",     4),
    ("theo@example.com",    "culture@example.com",  4),

    ("evie@example.com",    "cooking@example.com",  4),
    ("evie@example.com",    "yoga@example.com",     4),
    ("evie@example.com",    "wellness@example.com", 5),

    ("arthur@example.com",  "yoga@example.com",     4),
    ("arthur@example.com",  "wellness@example.com", 4),
    ("arthur@example.com",  "fitness@example.com",  5),

    ("poppy@example.com",   "cooking@example.com",  5),
    ("poppy@example.com",   "art@example.com",      5),
    ("poppy@example.com",   "food@example.com",     4),

    ("archie@example.com",  "comedy@example.com",   4),
    ("archie@example.com",  "fitness@example.com",  4),
    ("archie@example.com",  "music@example.com",    5),

    ("ivy@example.com",     "fitness@example.com",  4),
    ("ivy@example.com",     "culture@example.com",  5),
    ("ivy@example.com",     "wellness@example.com", 4),

    ("george@example.com",  "food@example.com",     4),
    ("george@example.com",  "culture@example.com",  5),
    ("george@example.com",  "network@example.com",  4),

    ("rosie@example.com",   "food@example.com",     5),
    ("rosie@example.com",   "culture@example.com",  4),
    ("rosie@example.com",   "art@example.com",      4),

    ("harry@example.com",   "yoga@example.com",     5),
    ("harry@example.com",   "wellness@example.com", 4),
    ("harry@example.com",   "fitness@example.com",  4),

    ("daisy@example.com",   "food@example.com",     5),
    ("daisy@example.com",   "art@example.com",      4),
    ("daisy@example.com",   "culture@example.com",  5),

    ("max@example.com",     "comedy@example.com",   4),
    ("max@example.com",     "fitness@example.com",  5),
    ("max@example.com",     "music@example.com",    4),
]


#Get images from Picsum

def addSampleImages(event, count=3):
    for i in range(1, count + 1):
        imageNumber = ((event.id * 10) + i) % 2000
        if imageNumber == 0:
            imageNumber = 2000

        imageUrl = f"https://yavuzceliker.github.io/sample-images/image-{imageNumber}.jpg"
        response = requests.get(imageUrl)

        if response.status_code == 200:
            photo = EventPhoto(
                event=event,
                caption=f"{event.title} — photo {i}",
                order=i
            )
            photo.image.save(
                f"event_{event.id}_{i}.jpg",
                ContentFile(response.content),
                save=True
            )




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
        print("Added business:", businesses[b["email"]].displayName)


    customers = {}
    for c in customerAccounts:
        acc = Account.objects.create(
            email=c["email"], 
            password=hashedPassword, 
            accountType="customer"
            )
        
        customers[c["email"]] = Customer.objects.create(accountId=acc, name=c["name"])

        print("Added customer:", customers[c["email"]].name)


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

        addSampleImages(event, 3)
        print("Added event:", event.title)

    for customerEmail, eventTitle in bookingData:
        
        event = events[eventTitle]
        booking = Books(customerId=customers[customerEmail], eventId=event)
        booking.save()
        event.save()
        print("Added booking:", customers[customerEmail].name, "->", event.title)

    for customerEmail, businessEmail, rating in ratingData:
        Rates.objects.create(
            customerId=customers[customerEmail],
            businessId=businesses[businessEmail],
            rating=rating,
        )
        print("Added rating:", customers[customerEmail].name, "->", businesses[businessEmail].displayName, ":", rating)


if __name__ == "__main__":
    populate()
