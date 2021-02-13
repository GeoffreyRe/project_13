from django.urls import path, include
from translations import views

# we split urlpatterns because a part of urls is dependent of project urls (see include in urls.py of project app)
# the second iterable is not dependent of project app and is included in the main urls.py module (in odoo_translations folder)
urlpatterns_with_project = [
    path('<str:instance_type>', views.instance_translation_list, name="instances_list"),
    path('<str:instance_type>/<int:instance_id>', views.instance_translations, name="instance_translations"),
    path('<str:instance_type>/all', views.all_instance_translations, name="all_instance_translations")
]

urlpatterns_without_project = [
    path('get_translations/', views.get_block_translation, name="get_block_translation"),
    path('save_translations_changes/', views.save_translations_changes, name="save_translations_changes")
]