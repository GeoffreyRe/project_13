from django.urls import path
from . import views

urlpatterns = [
    path("signup", views.view_signup, name="signup")
]