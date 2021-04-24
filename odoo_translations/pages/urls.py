from django.urls import path
from . import views

urlpatterns = [
    path("home", views.view_home, name="view_home"),
    path("legal_notice", views.view_legal_notice, name="legal_notice")
]