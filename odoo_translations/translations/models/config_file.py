import os
import logging
from django.db.models.signals import post_delete
from django.db import models
from django.apps import apps
from django.dispatch import receiver
from translations.exceptions import NoTranslationFoundInFileError, NoOdooTranslationFileHeader, TranslationBlockStructureNotGoodError

logger = logging.getLogger(__name__)

class ConfigFile(models.Model):
    """
    This model represents configuration file of a project
    """
    CONFIG_TYPES = [
        ('model', 'Model')
    ]

    #  type of configuration file
    name = models.CharField(max_length=40, null=False, blank=True)
    type = models.CharField(max_length=40, 
                            null=False,
                            choices=CONFIG_TYPES)
    
    # the project related to this file
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name="config_files",
        null=False
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)

    def get_file_location(instance, filename):
        """
        This method returns the location where the file must be located.
        instance : instance of the config_file
        filename : the name of the file that has been uploaded
        """
        project_directory_name = str(instance.project.id) + "_" + instance.project.name
        
        return "config_files/{0}/{1}".format(project_directory_name, filename)
    
    file = models.FileField(upload_to=get_file_location, null=False)


    def analyze(self):
        if self.type == "model":
            InstanceType = apps.get_model('translations', 'InstanceType')
            Instance = apps.get_model('translations', 'Instance')
            model_type = InstanceType.objects.filter(name="ir.model")
            if model_type:
                model_type = model_type[0]
            # for the moment, we will just handle model type
            # the file contains all of odoo models of project
            # it is a simple text file, and inside, a list of model separate by a newline character
            with open(self.file.path, "r", encoding="utf-8") as f:
                # readlines() will split all the lines of the file and put them in a list
                models_list = f.readlines()

                for model_name in models_list:
                    model_name = model_name.strip().replace('.', '_')
                    if model_name:
                        # if model_name is not empty
                        # we will look if a model instance already exists, else we create it
                        model_instance = Instance.objects.get_or_create(name=model_name,
                                                instance_type=model_type,
                                                project=self.project)
    
    class Meta:
        # rename table created by django in db
        db_table="config_file"







@receiver(post_delete, sender=ConfigFile)
def delete_file_associated_with_config_file(sender, instance, **kwargs):
    """
    This function will delete the file associated with ConfigFile
    """
    if (instance.file is not None) and os.path.exists(os.path.abspath(instance.file.path)):
        absolute_path = os.path.abspath(instance.file.path)
        # si l'instance a un fichier de config associé et que le chemin est bon
        if os.path.isfile(absolute_path):
            # on vérifie que c'est bien un fichier
            # on supprime le fichier
            try:
                os.remove(absolute_path)
                logger.info("le fichier de l'instance {} a bien été supprimée".format(instance))
            except OSError:
                logger.error("Un problème est survenu lors de la suppression du fichier de {}".format(instance))
        else:
            logger.error("Le chemin spécifié pour l'instance {} correspond à un dossier".format(instance))
    else:
        logger.error("L'instance {} n'a pas de fichier lié ou le chemin spécifié pour le fichier n'existe pas".format(instance))