from django.urls import path
from . import views

urlpatterns = [
    path('', views.discover, name='discover'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('contact/', views.contact, name='contact'),
    path("events/<int:event_id>/", views.event_detail, name="event_detail")
]
