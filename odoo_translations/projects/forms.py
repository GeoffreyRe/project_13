from django.forms import ModelForm
from .models import Project, Role


class ProjectCreationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # we iterate through self.fields.items() to add class to each fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'creation_date':
                field.widget.attrs['disabled'] = True

    class Meta:
        model = Project
        fields = ['name', 'description', 'creation_date']


class RoleForm(ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'id']
