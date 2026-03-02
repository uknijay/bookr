from django.db import models

from django.conf import settings

class Business(models.Model):
    #INCOMPLETE: This is just made as a placeholder to make the event model work.

    account = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="business",
    )

    displayName = models.CharField(max_length=120)

    def __str__(self):
        return self.displayName
    
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    maxCapacity = models.PositiveIntegerField()
    currentCapacity = models.PositiveIntegerField(default=0)

    location = models.CharField(max_length=255)
    date = models.DateTimeField()

    #TODO: This may need to be changed after merging with the actual business model.
    organiser = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="organised_events",
    )

    def __str__(self):
        return self.title


class EventPhoto(models.Model):
    event = models.ForeignKey(Event,on_delete=models.CASCADE,related_name="photos",)
    image = models.ImageField(upload_to="event_photos/")
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Photo for {self.event.title}"
