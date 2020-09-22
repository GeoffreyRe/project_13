from django.urls import path
from . import views

urlpatterns = [
    path("signup", views.view_signup, name="signup"),
    path('login', views.view_login, name="login"),
    path('logout', views.view_logout, name="logout" )
]