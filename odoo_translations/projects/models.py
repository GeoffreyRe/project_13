from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import User
from .managers import CustomProjectManager

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

    def __str__(self):
        return self.get_name_display()

class Project(models.Model):
    """
    This model is projects created by user when he wants to handle some translations
    """
    name = models.CharField(max_length=40, null=False, blank=False, verbose_name="Nom du projet")
    description = models.TextField(blank=True)
    # creator is a many-to-one field thats links to the user who creates the project
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="projects_created"
    )
    creation_date = models.DateTimeField(default=timezone.now, null=False, verbose_name="Date de création")
    template_file = models.OneToOneField('translations.TranslationFile',
                                        on_delete=models.SET_NULL,
                                        related_name="project_where_template",
                                        null=True,
                                        blank=True)
    objects = CustomProjectManager()
    
    def __str__(self):
        return self.name


class Invitation(models.Model):

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="project_invitations",
        null=False
    )
    user_role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=False
    )
    accepted= models.BooleanField(
        null=True,
        default=None
    )
    inviting_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="project_invitations_send"
    )

    def __str__(self):
        return "Invitation projet {} : {} invite {} en tant que {}".format(self.project.name,
                                                                        self.inviting_user.username,
                                                                        self.user.username,
                                                                        self.user_role.name)

class UserProject(models.Model):
    """
    This model is a ManyToMany table between User and Project. Indeed,
    each user can work on many projects and one project can have many users.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False
    )
    user_role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=False
    )
    invitation = models.OneToOneField(
        Invitation,
        on_delete=models.PROTECT,
        null=True,
        related_name="project_linked"
    )

    def __str__(self):
        return "l'utilisateur {} a le rôle {} sur le projet \"{}\"".format(self.user.username, 
                                                                            self.user_role.get_name_display(), self.project.name)

    class Meta:
        # we want to make the tuple (project_id, user_id) a composite primary_key
        # but Django does not support composite PK so we use unique_togheter
        # to make sure project_id and user_id are unique
        unique_together = [("project_id", "user_id")]
        # custom database name for table
        db_table = "projects_user_project"
        
