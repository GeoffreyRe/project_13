from django.contrib import admin
from .models import Project, Role, Invitation, UserProject

admin.site.register(Project)
admin.site.register(Role)
admin.site.register(Invitation)
admin.site.register(UserProject)


# Register your models here.
