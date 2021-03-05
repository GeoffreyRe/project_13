import os
import logging
from django.db.models.signals import post_delete
from django.db import models
from django.apps import apps
from django.dispatch import receiver
from translations.exceptions import FileParsingError


logger = logging.getLogger(__name__)

# Create your models here.
class TranslationFile(models.Model):
    """
    This model represents project's translation files.
    """
    TRANSLATED_LANGAGES = [
        ('fr', 'Français'),
        ('ndlr', 'Néerlandais')
    ]
    # file name of file.
    # by default, if will be the name of the original file but it can be changed
    name = models.CharField(max_length=40, null=False, blank=True)
    is_template = models.BooleanField(default=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name="translation_files",
        null=False
    )
    # the language that the file translates. If template, can be null.
    translated_language = models.CharField(max_length=40, 
                                            null=True,
                                            choices=TRANSLATED_LANGAGES)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = os.path.basename(self.original_file.name)
        super().save(*args, **kwargs)

    
    def analyze_content(self):
        """
        This method will analyse content of the file related with the instance of TranslationFile

        -----------
        Logique à appliquer :
        Méthode analyze_file va extraire du fichier, les blocs le composant
        pour chaque bloc, on va appeler une méthode sur l'objet bloc en lui passant le contenu du bloc
        """
        
        with open(self.original_file.path, "r", encoding="utf-8") as f:
            # readlines() will split all the lines of the file and put them in a list
            content = f.readlines()
            blocks = []
            last_block = 0
            # we will try to separate each block found
            for i, content_line in enumerate(content):
                # with strip method, we remove white spaces + line breaks
                # warning : with this method : there must have a space at the end of file.
                # otherwise, the last block won't be taken into account
                content[i] = content_line.strip()
                if content[i] == "":
                    blocks.append({'block' : content[last_block:i], 'position': last_block + 1})
                    last_block = i + 1
            # now we will check if there is the header and if there is min 2 blocks (header + a traduction block)

            # warning : with this method : there must have a space at the end of file.
            # otherwise, the last block won't be taken into account, so we could do this way
            if content[-1].strip() != "":
                blocks.append({'block' : content[last_block:], 'position': last_block + 1})

            if len(blocks) < 2:
                raise FileParsingError("Aucun block de traduction n'a été trouvé dans le fichier {}".format(self.name))
            
            TranslationBlock = apps.get_model('translations', 'TranslationBlock')
            # check of first block wich must be header :
            header_content = blocks[0]['block']
            errors = TranslationBlock.check_errors_content(header_content, 1, file_name=self.name,is_header=True)
            if errors[0] is True:
                raise FileParsingError(errors[1])
            
            # we save the header
            
            TranslationBlock.objects.create_block_from_data(header_content, file=self,is_header=True)
            
            # we will analyze each block found
            for index, block_infos in enumerate(blocks[1:]):
                block = block_infos['block']
                if block:
                    errors = TranslationBlock.check_errors_content(block, block_infos['position'], file_name=self.name)
                    if errors[0] is True:
                        raise FileParsingError(errors[1])
                    # if there is no errors, we will create the block
                    TranslationBlock.objects.create_block_from_data(errors[1], block_position=block_infos['position'],file=self)

            
            
                

    def get_file_location(instance, filename):
        """
        This method returns the location where the file must be located.
        instance : instance of the translation_file
        filename : the name of the file that has been uploaded
        """
        project_directory_name = str(instance.project.id) + "_" + instance.project.name
        
        return "translation_files/{0}/{1}".format(project_directory_name, filename)

    # file wich will be uploaded
    # warning : when an instance get deleted, the file is not deleted so we have to create
    # a method that deletes the file ! (see signals)
    original_file = models.FileField(upload_to=get_file_location, null=False)

    def __str__(self):
        return "fichier de traduction : {}".format(self.name)
    


    class Meta:
        # rename table created by django in db
        db_table="translation_file"

# we will create a function that receives a signal when an instance
# of TranslationFile is deleted. This function will delete the file
# associated with this instance because Django doesn't do it automatically.
@receiver(post_delete, sender=TranslationFile)
def delete_file_associated_with_TranslationFile(sender, instance, **kwargs):
    """
    This function will delete the file associated with TranslationFile
    """
    if (instance.original_file is not None) and os.path.exists(os.path.abspath(instance.original_file.path)):
        absolute_path = os.path.abspath(instance.original_file.path)
        # si l'instance a un fichier de traduction associé et que le chemin est bon
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

