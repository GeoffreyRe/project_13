from django.contrib import admin
from .models import TranslationFile, TranslationBlock, TranslationLine, LineType, Instance, InstanceType, ConfigFile

admin.site.register(TranslationFile)
admin.site.register(TranslationBlock)
admin.site.register(TranslationLine)
admin.site.register(LineType)
admin.site.register(Instance)
admin.site.register(InstanceType)
admin.site.register(ConfigFile)

# Register your models here.
