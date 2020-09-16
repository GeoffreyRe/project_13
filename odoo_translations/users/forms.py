from django.forms import ModelForm
from django.forms import PasswordInput
from .models import User

class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        # we iterate through self.fields.items() to add class to each fields
        for field_name, field in self.fields.items():
            if field_name =="password":
                field.widget = PasswordInput()
            field.widget.attrs['class'] = 'form-control'
    class Meta:
        model = User
        fields = ['username', 'email','password']
        help_texts = {
            'username' : ""
        }
        error_messages = {
            'email':{
                "unique": "Un utilisateur avec cet email existe déjà !"
            }
        }