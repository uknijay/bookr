from django.urls import path
from . import views

urlpatterns = [
    path('', views.discover, name='discover'),
    path('account/login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("events/<int:event_id>/book/", views.book_event, name="book_event")
]
