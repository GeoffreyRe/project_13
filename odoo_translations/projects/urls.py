from django.urls import path
from . import views

urlpatterns = [
    path('list', views.projects_list_view, name="projects_list"),
    path('invitations', views.invitations_list_view, name="invitations_list"),
    path('create', views.create_project, name="create_project")
]