from django.urls import path
from . import views

urlpatterns = [
    path('', views.discover, name='discover'),
    path('account/login/', views.user_login, name='login'),
    path('account/register/', views.register_choose, name='register_choose'),
    path('account/register/<str:accountType>/', views.register_user, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    path('business-account/', views.business_dashboard, name='business_dashboard'),
    path('business-account/my-events/', views.business_my_events, name='business_my_events'),
    path('business-account/my-events/upcoming-event/', views.business_upcoming_events, name='business_upcoming_events'),
    path('business-account/my-events/past-events/', views.business_past_events, name='business_past_events'),
    path('business-account/my-events/create-event/', views.business_create_event, name='business_create_event'),
    path('business-account/my-events/edit-event/<int:event_id>/', views.business_edit_event, name='business_edit_event'),
    path('business-account/my-events/<int:event_id>/stats/', views.business_event_stats, name='business_event_stats'),
    path('business-account/view-ratings/', views.business_view_ratings, name='business_view_ratings'),

    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("events/<int:event_id>/book/", views.book_event, name="book_event"),
    path("business/create-event/", views.create_event, name="create_event"),
    path("events/<int:event_id>/rate/", views.rate_event, name="rate_event"),
    path("events/<int:event_id>/unbook/", views.unbook_event, name="unbook_event"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
]
