from django.contrib import admin

from main.models import Business
from main.models import Event
from main.models import EventPhoto 

admin.site.register(Business)
admin.site.register(Event)
admin.site.register(EventPhoto)