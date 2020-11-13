import os
import logging
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.apps import apps
from .exceptions import NoTranslationFoundInFileError, NoOdooTranslationFileHeader




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
        """
        with open(self.original_file.path, "r", encoding="utf-8") as f:
            # readlines() will split all the lines of the file and put them in a list
            content = f.readlines()
            blocks = []
            last_block = 0
            # we will try to separate each block found
            for i, content_line in enumerate(content):
                # with strip method, we remove white spaces + line breaks
                content[i] = content_line.strip()
                if content[i] == "":
                    blocks.append(content[last_block:i])
                    last_block = i + 1
            # now we will check if there is the header and if there is min 2 blocks (header + a traduction block)

            if len(blocks) < 2:
                raise NoTranslationFoundInFileError("Aucun block de traduction n'a été trouvé dans le fichier {}".format(self.name))

            # check of first block wich must be header :
            import pdb;pdb.set_trace()
            header_content = blocks[0]
            if header_content[0] != "# Translation of Odoo Server.":
                raise NoOdooTranslationFileHeader("Erreur lors de l'analyse du fichier : ligne 1 --- le premier bloc n'est pas le header")

            # we save the header
            TranslationBlock = apps.get_model('translations', 'TranslationBlock')
            header_block = TranslationBlock(
                file=self,
                is_header=True,
                raw_text="\n".join(blocks[0])
            )

            header_block.save()

            # we will analyze each block found
            for block in blocks[1:]:
                pass
                # translation block must begins with a line that specifies the module
                #TODO: checker la première ligne : si ce n'est pas par rapport au module == Erreur
                # ensuite retrouver le module qui correspond si il existe dans les "instances", sinon le créer
                # Ensuite retrouver les msgstr et msgid du block ---> si pas trouvé ou vide (pour les non templates) == Erreur
                # Enfin, créer pour chaque ligne, une TranslationLine. Si problème == Erreur 



    


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

class TranslationBlock(models.Model):
    file = models.ForeignKey(TranslationFile,
                            on_delete=models.CASCADE,
                            null=False,
                            related_name="translation_blocks")
    raw_text = models.TextField(null=False)
    is_header = models.BooleanField(default=False)
    original_text = models.TextField(null=True, blank=True)
    translated_text = models.TextField(null=True)

    def __str__(self):
        return "block de traduction numéro {} du fichier {}".format(self.id, self.file.name)

class LineType(models.Model):
    """
    These model defines the type of translation line. It indicates 
    what is the attribute of the instance the line translates.

    The current types are the folowing :
    - field_description
    - help
    - name
    - code_line
    - other
    """
    name = models.CharField(max_length=40,
                            null=False,
                            blank=False,
                            unique=True)
    def __str__(self):
        return "type de ligne : {}".format(self.name)
class InstanceType(models.Model):
    """
    This model defines the type of an instance
    the current types are the following :
    - module
    - ir_model
    - ir.model.field
    - ir.ui.view
    - ir.ui.menu
    - ir.actions.act_window
    - ir.code
    - ir.code.position
    - other
    """
    name = models.CharField(max_length=60,unique=True)

    def __str__(self):
        return "type d'instance : {}".format(self.name)

class Instance(models.Model):
    """
    This model defines the instances that are inside a file
    For example :
    For a module : Belcco, Sale, etc...
    For a odoo model : res.partner, sale.order, etc...
    for a field : net_price, quantity, etc...
    for a view : view_form_res_partner_id
    etc...
    """
    name = models.CharField(max_length=60, null=False, blank=False)
    instance_type = models.ForeignKey(
                                    InstanceType,
                                    on_delete= models.PROTECT,
                                    null=False
                                    )
    parent= models.ForeignKey(
                            "self",
                            on_delete = models.CASCADE,
                            related_name="instance_childs",
                            null=True,
                            blank=True
                            )
    def __str__(self):
        sentence = "instance {} de type {}".format(self.name, self.instance_type.name)
        if self.parent is not None:
            sentence += " et enfant de l'instance {} (type {})".format(self.parent.name, self.parent.instance_type.name)

        return sentence

class TranslationLine(models.Model):
    block = models.ForeignKey(TranslationBlock,
                            on_delete=models.CASCADE,
                            related_name="translation_lines")
    in_translation_file = models.BooleanField(null=False)
    in_template_file = models.BooleanField(null=True)
    line_type = models.ForeignKey(
                                LineType,
                                on_delete=models.PROTECT,
                                related_name="translation_lines",
                                null=False
                                )
    instance = models.ForeignKey(
        Instance,
        on_delete=models.PROTECT,
        blank=False,
        null=False
        )
    
    def __str__(self):
        return "ligne de traduction numéro {}".format(self.id)

