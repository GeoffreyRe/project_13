from django.forms import ModelForm
from .models import TranslationFile

class TranslationFileForm(ModelForm):

    class Meta:
        model = TranslationFile
        fields = ['id', 'name', 'translated_language', 'is_template','original_file']