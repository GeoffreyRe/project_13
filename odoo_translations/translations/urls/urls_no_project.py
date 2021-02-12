from django.urls import path, include
from translations import views
# urls that doesn't be linked to any project
urlpatterns = [
    path('get_translations/', views.get_block_translation, name="get_block_translation")
]