from django.db import models, transaction
from django.conf import settings
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.db.models import Avg
from django.contrib.auth.models import User
from django.utils import timezone   


class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
    # Constant = value in db , label for humans
    ("business", "Business"),
    ("customer", "Customer")
    ]

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255) # Store as hash value
    accountType = models.CharField(max_length=50,choices = ACCOUNT_TYPE_CHOICES, default ="customer")

    def __str__(self):
        return str(self.email) 
    
    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

class Business(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    displayName = models.CharField(max_length=50, 
                                   validators=[MinLengthValidator(2, message="The display name must be at least 2 characters")])

    @property
    def avgRating(self):
        result = Rates.objects.filter(businessId=self).aggregate(avg=Avg("rating"))
        return result["avg"]
    
    def __str__(self):
        return str(self.displayName or "Unnamed Business")

    class Meta:
        verbose_name = "Business"
        verbose_name_plural = "Businesses"
    
class Customer(models.Model):
    accountId = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=50, 
                            validators=[MinLengthValidator(2, message="The display name must be at least 2 characters")])
    
    def __str__(self):
        return str(self.name or "Unnamed Customer")

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"


class Event(models.Model):
    title = models.CharField(max_length=200, default="")
    description = models.TextField(blank=True, default="")

    maxCapacity = models.PositiveIntegerField(default=0)
    currentCapacity = models.PositiveIntegerField(default=0)

    venue = models.CharField(max_length=200, default="")
    venueAddress = models.CharField(max_length=200, default="")
    date = models.DateTimeField(default=timezone.now)
    date = models.DateTimeField()

    organiser = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="organised_events",
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"


class EventPhoto(models.Model):
    event = models.ForeignKey(Event,on_delete=models.CASCADE,related_name="photos",)
    image = models.ImageField(upload_to="event_photos/")
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ["order"]
        verbose_name = "Event Photo"
        verbose_name_plural = "Event Photos"


    def __str__(self):
        return f"Photo for {self.event.title}"
    
    

# M-N Customer <-> Business + rating
class Rates(models.Model):
    customerId = models.ForeignKey(Customer, on_delete=models.CASCADE)
    businessId = models.ForeignKey(Business, on_delete=models.CASCADE)

    rating = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])

    class Meta:
        unique_together = ("customerId","businessId")
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"

    def __str__(self):
        return f"{self.customerId} rated {self.businessId}: {self.rating}"

# M-N Customer <-> Event + date
class Books(models.Model):
    customerId = models.ForeignKey(Customer, on_delete=models.CASCADE)
    eventId = models.ForeignKey(Event, on_delete=models.CASCADE)
    
    bookingDate = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("customerId", "eventId")
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"


    def save(self, *args, **kwargs):
        # check if new boooking
        if not self.pk:
            with transaction.atomic():
                event = self.eventId
                # check if space
                if event.currentCapacity < event.maxCapacity:
                    event.currentCapacity += 1
                    event.save()
                else:
                    raise Exception("This event is full!")
        super().save(*args,**kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            event = self.eventId
            if event.currentCapacity > 0:
                event.currentCapacity -= 1
                event.save()
    
    def __str__(self):
        return f"{self.customerId} booked {self.eventId}"

