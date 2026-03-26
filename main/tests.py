from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Account, Business, Event


class PageAccessTests(TestCase):
    def setUp(self):
        self.businessAccount = Account.objects.create(
            email="business@test.com",
            password="testpass123",
            accountType="business",
        )

        self.business = Business.objects.create(
            account=self.businessAccount,
            displayName="Test Business",
        )

        self.event = Event.objects.create(
            title="Test Event",
            description="A test event",
            maxCapacity=20,
            currentCapacity=0,
            venue="Test Venue",
            venueAddress="123 Test Street",
            date=timezone.now() + timedelta(days=7),
            organiser=self.business,
        )

    def test_discover_page_loads(self):
        response = self.client.get(reverse("discover"))
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_register_choose_page_loads(self):
        response = self.client.get(reverse("register_choose"))
        self.assertEqual(response.status_code, 200)

    def test_register_customer_page_loads(self):
        response = self.client.get(reverse("register", args=["customer"]))
        self.assertEqual(response.status_code, 200)

    def test_register_business_page_loads(self):
        response = self.client.get(reverse("register", args=["business"]))
        self.assertEqual(response.status_code, 200)

    def test_event_detail_page_loads(self):
        response = self.client.get(reverse("event_detail", args=[self.event.id]))
        self.assertEqual(response.status_code, 200)

    def test_my_bookings_redirects_when_logged_out(self):
        response = self.client.get(reverse("my_bookings"))
        self.assertEqual(response.status_code, 302)

    def test_create_event_redirects_when_logged_out(self):
        response = self.client.get(reverse("create_event"))
        self.assertEqual(response.status_code, 302)

    def test_business_my_events_redirects_when_logged_out(self):
        response = self.client.get(reverse("business_my_events"))
        self.assertEqual(response.status_code, 302)

    def test_business_event_stats_redirects_when_logged_out(self):
        response = self.client.get(reverse("business_event_stats", args=[self.event.id]))
        self.assertEqual(response.status_code, 302)

    def test_business_view_ratings_redirects_when_logged_out(self):
        response = self.client.get(reverse("business_view_ratings"))
        self.assertEqual(response.status_code, 302)