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
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("events/<int:event_id>/book/", views.book_event, name="book_event"),
    path("business/create-event/", views.create_event, name="create_event"),
    path("events/<int:event_id>/rate/", views.rate_event, name="rate_event"),
    path("events/<int:event_id>/unbook/", views.unbook_event, name="unbook_event"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("business/my-events/", views.business_my_events, name="business_my_events"),
    path("business/my-events/<int:event_id>/stats/", views.business_event_stats, name="business_event_stats"),
    path("business/view-ratings/", views.business_view_ratings, name="business_view_ratings"),
]
