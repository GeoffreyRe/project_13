from django.db import models ,IntegrityError, transaction
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.apps import apps
from users.models import User
from .managers import CustomProjectManager
from projects.utils import regroup_lines_by_block
from translations.exceptions import NoFileForProjectError, FileParsingError

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
            if values.get('config_file', None):
                self.add_files_to_project([values['config_file']], config_file=True)
            self.delete_files_of_project(values['files_to_delete'])
            self.delete_files_of_project(values['config_files_to_delete'], config_files=True)
    
    def delete_users_on_project(self, user_ids):
        self.userproject_set.filter(pk__in=user_ids).delete()

    def add_files_to_project(self, files, config_file=False):
        for file in files:
            if config_file is True:
                new_file = apps.get_model('translations', 'ConfigFile')(
                    project=self,
                    type="model",
                    file=file
                )
                new_file.save()
            else:
                TranslationFileModel = apps.get_model('translations', 'TranslationFile')
                new_file = TranslationFileModel(
                    project=self,
                    translated_language=file['lang'],
                    is_template=file['template'],
                    original_file=file['file']
                )
                new_file.save()
    
    def delete_files_of_project(self, files_ids, config_files=False):
        for file_id in files_ids:
            if config_files is True:
                try:
                    file_to_delete = apps.get_model('translations', 'ConfigFile').objects.get(id=int(file_id))
                except DoesNotExist:
                    pass
            else:
                TranslationFileModel = apps.get_model('translations', 'TranslationFile')
                try:
                    file_to_delete = TranslationFileModel.objects.get(id=int(file_id))
                except DoesNotExist:
                    pass
            
            
            file_to_delete.delete()
    
    def delete_translations(self):
        """
        This method will delete all translations of project
        """
        # first we delete translation blocks
        for file in self.translation_files.all():
            file.translation_blocks.all().delete()
        
        # then instance
        Instance = apps.get_model('translations', 'Instance')

        Instance.objects.filter(project=self).delete()

        self.save()
        
    
    def analyze_translation_files(self):
        """
        This method will launch analysis of every translation files of a project
        """
        if len(self.translation_files.all()) == 0:
            # check if there is at least one translation file to analyse.
            # TODO: check if there is not only a .pot file. We need at least a .po file
            raise FileParsingError("Il n'y a pas de fichier de traduction à analyser pour ce projet")

        for config_file in self.config_files.all():
            config_file.analyze()
        
        for translation_file in self.translation_files.all():
            translation_file.analyze_content()

    def all_instances(self, type="ir.model"):
        instances = []
        InstanceType = apps.get_model('translations.InstanceType')
        Instance = apps.get_model('translations.Instance')
        instance_type = InstanceType.objects.get(name=type)
        for instance in Instance.objects.filter(project=self.id, instance_type=instance_type):
            instances.append({
                'instance': instance,
                'nb_fr': instance.get_number_of_translations(),
                'nb_ndlr': instance.get_number_of_translations(lang='ndlr')
            })
        return instances
    
    def translations_instances(self, instance_id=False, with_children=True, type=False):
        """
        Retrieve all translations from instance associated with this project
        if instance_id is given, only find translations for this particular model
        if with_fields is True, then retrieve also translations of fields wich are 'children' of models
        else, only find translations for the model.
        """
        Instance = apps.get_model('translations.Instance')
        TranslationLine = apps.get_model('translations.TranslationLine')
        
        if instance_id is not False:
            instance = Instance.objects.get(id=instance_id)
            query = Q(instance=instance)
            if with_children: 
                # if with_children is True, then we add instances that are children of model (its fields)
                children_instances = Instance.objects.filter(parent=instance)
                query = query | Q(instance__in=children_instances)
            
            blocks_lang = {}
            for lang in ['fr', 'ndlr']:
                blocks_of_lang = self.translation_files.filter(translated_language=lang).values_list('translation_blocks', flat=True)
                translation_lines = TranslationLine.objects.filter(query & Q(block__in=blocks_of_lang))
                blocks = regroup_lines_by_block(translation_lines)
                blocks_lang[lang] = blocks
            return (instance, blocks_lang)
        
        if type is not False:
            instances = self.all_instances(type=type)
            query = Q(instance__in=[instance['instance'] for instance in instances])
            if with_children:
                children_instances = Instance.objects.filter(parent__in=[instance['instance'] for instance in instances])
                query = query | Q(instance__in=children_instances)

            blocks_lang = {}
            for lang in ['fr', 'ndlr']:
                blocks_of_lang = self.translation_files.filter(translated_language=lang).values_list('translation_blocks', flat=True)
                translation_lines = TranslationLine.objects.filter(query & Q(block__in=blocks_of_lang))
                blocks = regroup_lines_by_block(translation_lines)
                blocks_lang[lang] = blocks
            
            return (instances, blocks_lang)

    def export_translations(self, lang):
        """
        This method will concatenate every translation related to the project
        """
        #TODO: exporter une string représentant le contenu du fichier de traduction
        content = ("# Translation of Odoo Server.\n"
                    "# This file contains the translation of the following modules:\n"
                    "#	* belcco\n"
                    "#\n"
                    "msgid \"\"\n"
                    "msgstr \"\"\n"
                    "\"Project-Id-Version: Odoo Server 11.0+e\"\n"
                    "\"Report-Msgid-Bugs-To: \"\n"
                    "\"POT-Creation-Date: 2020-10-23 11:16+0000\"\n"
                    "\"PO-Revision-Date: 2020-10-23 11:16+0000\"\n"
                    "\"Last-Translator: <>\"\n"
                    "\"Language-Team:\"\n"
                    "\"MIME-Version: 1.0\"\n"
                    "\"Content-Type: text/plain; charset=UTF-8\"\n"
                    "\"Content-Transfer-Encoding:\"\n"
                    "\"Plural-Forms:\"\n\n")
        
        for file in self.translation_files.filter(translated_language=lang):
            for block in file.translation_blocks.filter(is_header=False):
                module_line = block.translation_lines.filter(instance__instance_type__name='module')
                module_name = module_line[0].instance.name.strip() if (module_line and module_line[0].instance) else ""
                for line in block.translation_lines.all():
                    if line.instance.instance_type.name == "module":
                        content += "#. module: {}".format(module_name)
                    elif line.instance.instance_type.name == "code.position":
                        content += "#: code:{}:{}".format(line.instance.parent.name, line.instance.name)
                    elif line.instance.instance_type.name in ['ir.model', 'ir.ui.view', 'ir.ui.menu', 'ir.actions.act_window']:
                        content += "#: model:{},{}:{}.{}".format(line.instance.instance_type.name,
                                                                line.line_type.name, module_name, line.instance.name)
                    elif line.instance.instance_type.name == 'ir.model.fields':
                        content += "#: model:{},{}:{}.field_{}_{}".format(line.instance.instance_type.name,
                                                                line.line_type.name, module_name, line.instance.parent.name, line.instance.name)
                    elif line.instance.instance_type.name == "other":
                        content += line.instance.name
                    
                    content += "\n"
                content += "msgid \"{}\"".format(block.original_text) + "\n"
                content += "msgstr \"{}\"".format(block.translated_text) + "\n\n"

        return content
                


        



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
        self.save()
    
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
        
