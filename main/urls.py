from django.urls import path
from . import views

urlpatterns = [
    path('', views.discover, name='discover'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("register/", views.register_view, name="register"),
    path("profile/", views.profile_view, name="profile"),

]
