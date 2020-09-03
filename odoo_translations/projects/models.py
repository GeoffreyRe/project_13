from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Role(models.Model):
    """
    This model consists of the role of an user when he works on a project.
    The role has an important part when the user wants to make some actions
    """
    DEVELOPER = "DEV"
    TRANSLATOR = "TRA"
    NAME_CHOICES = [
        (DEVELOPER, "Développeur"),
        (TRANSLATOR, "Traducteur")
    ]
    # define de name of the role.
    name = models.CharField("Nom du rôle",
                            max_length=3,
                            choices=NAME_CHOICES,
                            unique=True)

    def save(self, *args, **kwargs):
        """
        We overwrite the save method to run validators before saving.
        """
        self.full_clean()
        super().save(*args, **kwargs)
        
