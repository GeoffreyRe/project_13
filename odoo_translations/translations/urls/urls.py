from django.urls import path, include
from translations import views

urlpatterns = [
    path('<str:instance_type>', views.instance_translation_list, name="instances_list"),
    path('<str:instance_type>/<int:instance_id>', views.instance_translations, name="instance_translations"),
    path('<str:instance_type>/all', views.all_instance_translations, name="all_instance_translations"),
    path('<str:instance_type>/all', views.all_instance_translations, name="all_instance_translations")
]