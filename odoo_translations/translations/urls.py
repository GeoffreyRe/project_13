from django.urls import path, include
from . import views

urlpatterns = [
    path('models', views.model_translation_list, name="model_list"),
    path('models/<int:model_id>', views.model_translations, name="model_translations")
]