from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import User

# Create your models here.
class NameValues(models.TextChoices):
    """
    This class determines the possible choices for the field "name" of Role model.
    """
    DEVELOPER = 'DEV', 'Développeur'
    TRANSLATOR = 'TRA', 'Traducteur'

class Role(models.Model):
    """
    This model consists of the role of an user when he works on a project.
    The role has an important part when the user wants to make some actions
    """
    # define de name of the role.
    name = models.CharField("Nom du rôle",
                            max_length=3,
                            choices=NameValues.choices,
                            unique=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(name__in=[choice for choice in NameValues.values]),
                name="valid_name_value")
        ]

class Project(models.Model):
    """
    This model is projects created by user when he wants to handle some translations
    """
    name = models.CharField(max_length=40, null=False, blank=False)
    description = models.TextField( blank=True)
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    creation_date = models.DateTimeField(default=timezone.now, null=False)


    #TODO: créer un champ template_file qui sera une clef étrangère vers le modèle
    # Translation_file
        
