from django.contrib import admin
from main.models import *


admin.site.register([Account, Business, Customer, Event, EventPhoto, Books, Rates])