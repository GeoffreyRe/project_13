from django.db import models, IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.apps import apps
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
                            unique=True,
                            blank=False,
                            null=False)

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
    objects = CustomProjectManager()
    
    def __str__(self):
        return self.name
    
    def modify_name(self, new_name):
        self.name = new_name
        self.save()
    
    def modify_description(self, new_description):
        self.description = new_description
        self.save()

    def send_invitation_to_project(self, email, role, inviting_user):
        InvitationModel = apps.get_model('projects', 'Invitation')
        UserModel = apps.get_model('users', 'User')
        RoleModel = apps.get_model('projects', 'Role')
        role_to_attribute = RoleModel.objects.get(name=role)
        new_user = UserModel.objects.get(email=email)
        new_invitation = InvitationModel(
            project=self,
            user=new_user,
            inviting_user=inviting_user,
            user_role=role_to_attribute
        )
        new_invitation.save()
    
    def modify_roles_of_user_on_project(self, values, user):
        for user_dict in values:
            if user_dict['id'] == "new":
                self.send_invitation_to_project(user_dict['email'], user_dict['role'], inviting_user=user)
            else:
                user_project = self.userproject_set.get(id=user_dict['id'])
                user_project.modify_user_role(user_dict['role'])
    
    def update_project(self, values, user):
        with transaction.atomic():
            project_values = values['infos_user']
            self.modify_name(project_values['project']['name'])
            self.modify_description(project_values['project']['description'])
            self.modify_roles_of_user_on_project(project_values['users'], user)
            self.delete_users_on_project(project_values['users_to_delete'])
            self.add_files_to_project(values['files'])
            self.delete_files_of_project(values['files_to_delete'])
    
    def delete_users_on_project(self, user_ids):
        self.userproject_set.filter(pk__in=user_ids).delete()

    def add_files_to_project(self, files):
        for file in files:
            TranslationFileModel = apps.get_model('translations', 'TranslationFile')
            new_file = TranslationFileModel(
                project=self,
                translated_language=file['lang'],
                is_template=file['template'],
                original_file=file['file']
            )
            new_file.save()
    
    def delete_files_of_project(self, files_ids):
        for file_id in files_ids:
            TranslationFileModel = apps.get_model('translations', 'TranslationFile')
            try:
                file_to_delete = TranslationFileModel.objects.get(id=int(file_id))
            except DoesNotExist:
                pass
            
            file_to_delete.delete()
            



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
        null=False,
        blank=False
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

    def is_accepted(self):
        self.accepted = True
    
    def is_refused(self):
        self.accepted = False
    
    def from_invitation_to_project(self):
        self.is_accepted()
        UserProject = apps.get_model('projects', 'UserProject')
        new_user_project = UserProject(project=self.project,
            user=self.user,
            user_role=self.user_role,
            invitation= self
        )
        try:
            new_user_project.save()
        except IntegrityError:
            return False
        self.save()
        return True


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

    def modify_user_role(self, new_role_id):
        new_role = Role.objects.get(id=new_role_id)
        self.user_role = new_role
        self.save()

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
        
