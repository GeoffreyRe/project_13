from django.urls import path, include
from . import views

urlpatterns = [
    path('list', views.projects_list_view, name="projects_list"),
    path('invitations', views.invitations_list_view, name="invitations_list"),
    path('create', views.create_project, name="create_project"),
    path('project_exists', views.view_verification_project_name, name="project_exists"),
    path('invitation/to-project', views.from_invitation_to_project, name="to-project"),
    path('invitation/refused', views.invitation_refused, name='invitation_refused'),
    path('<int:project_id>/details', views.detail_project, name="detail_project"),
    path('<int:project_id>/details/modifications', views.detail_project_modifications, name="detail_project_modifications"),
    path('<int:project_id>/modify_project', views.modify_project, name="modify_project"),
    path('users_exists', views.check_if_users_can_be_added_to_project, name="check_if_user_on_project"),
    path('<int:project_id>/translations/', include('translations.urls.urls'))
]