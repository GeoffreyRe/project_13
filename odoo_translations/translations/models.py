import os
import logging
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.apps import apps
from .exceptions import NoTranslationFoundInFileError, NoOdooTranslationFileHeader, TranslationBlockStructureNotGoodError
from .managers import CustomTranslationBlockManager



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
                    blocks.append(content[last_block:i])
                    last_block = i + 1
            # now we will check if there is the header and if there is min 2 blocks (header + a traduction block)

            # warning : with this method : there must have a space at the end of file.
            # otherwise, the last block won't be taken into account, so we could do this way
            if content[-1].strip() != "":
                blocks.append(content[last_block:])

            #import pdb;pdb.set_trace()

            if len(blocks) < 2:
                raise NoTranslationFoundInFileError("Aucun block de traduction n'a été trouvé dans le fichier {}".format(self.name))
            
            TranslationBlock = apps.get_model('translations', 'TranslationBlock')
            # check of first block wich must be header :
            header_content = blocks[0]
            errors = TranslationBlock.check_errors_content(header_content, 1, is_header=True)
            if errors[0] is True:
                raise NoOdooTranslationFileHeader(errors[1])
            
            # we save the header
            
            TranslationBlock.objects.create_block_from_data(header_content, file=self,is_header=True)

            # we will analyze each block found
            line_position = len(blocks[0]) + 1# line position will be displayed if errors occur.
            for block in blocks[1:]:
                errors = TranslationBlock.check_errors_content(block, line_position)
                if errors[0] is True:
                    raise TranslationBlockStructureNotGoodError(errors[1])
                # if there is no errors, we will create the block
                TranslationBlock.objects.create_block_from_data(errors[1], file=self)

            
            
                

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
    objects = CustomTranslationBlockManager()

    def __str__(self):
        return "block de traduction numéro {} du fichier {}".format(self.id, self.file.name)


    @staticmethod
    def find_lines_infos(translation_lines):
        """
        This method will make a loop over the list of lines given to the function
        and for each line, we will determine type of line, type of instance, ...
        """
        lines_infos = []
        for line in translation_lines:
            # for each line
            line_infos = {"line": line}
            line_parts = line.split(',')
            if len(line_parts) == 1:
                if line_parts[0].startswith('#. module:'):
                    line_infos["instance"] = {
                        "type": "module",
                        "name": line[10:]
                    }
                    line_infos["line_type"] = "name"

                elif line_parts[0].startswith('#: code:'):
                    line_infos["instance"] = {
                        "type": "code",
                        "name": line[8:]
                    }
                    line_infos["line_type"] = "code"
                
                else:
                    line_infos["instance"] = False

            elif len(line_parts) == 2:
                if line_parts[0] in ["#: model:ir.model",
                "#: model:ir.model.fields", "#: model:ir.ui.menu",
                "#: model:ir.actions.act_window", "#: model:ir.ui.view"]:
                    line_instance = line_parts[1].split(':')
                    if len(line_instance) == 2:
                    
                        line_infos["instance"] = {
                        "type": line_parts[0][9:],
                        "name": line_instance[1]
                        }
                        line_infos["line_type"] = line_instance[0]
                    else:
                        line_infos["instance"] = False


                        
                else:
                    line_infos["instance"] = False
            else:
                line_infos["instance"] = False
            
            lines_infos.append(line_infos)
        
        return lines_infos


    @staticmethod
    def check_errors_content(data, line, is_header=False):
        """
        data ==> text content of block, given as a list of lines
        is_header ==> if True, it a header block, checking is different
        line ==>
        This method will check if there are errors in block structure
        if yes: --> return error message
        if no: --> return False 
        """
        if is_header:
            if data[0] != "# Translation of Odoo Server.":
                return (True, "Erreur lors de l'analyse du fichier : ligne {} --- le premier bloc n'est pas le header".format(line))
            else:
                return (False,)

        # if it is a simple translation block
        if len(data) < 4:
                # if length of block is below 4, then it means that the block structure is not good.
                # Indeed, we need, for a block at least 4 lines : one for the module specification,
                # at least one for a instance to translate (translation line), and 2 for the sentence to translate
                # msgstr and msgid
                return (True,
            "ligne {} : la structure du bloc n'est pas conforme -> taille du bloc inférieur à 4 lignes".format(line))
        
        # the first line of block should be the module specification line
        supported_lines = []
        module_spec_line = data[0]
        if not module_spec_line.startswith("#. module:"):
            return (True,
            "ligne : {} --> ligne de specification du module attendue mais non trouvée".format(line))
        # we extract module name from module specification line
        supported_lines.append(module_spec_line.strip())
        
        # now we have to find msgid and msgstr
        msgid_text = None
        msgstr_text = None

        for pos, line in enumerate(data[1:]):
            # now we will try to see if we could find msgid and msgstr, else we raise error
            if line.startswith('msgid "'):
                msgid_text = []
                msgid_text.append(line[6:].strip())
                i = 1
                if (pos + i) < len(data[1:]):
                    next_line = data[1:][pos + i]
                else:
                    next_line = ""

                while next_line.startswith('"'):
                    msgid_text.append(next_line.strip())
                    i += 1
                    if (pos + i) < len(data[1:]):
                        next_line = data[1:][pos + i]
                    else:
                        next_line = ""
                        
            elif line.startswith('msgstr "'):
                if msgid_text is None:
                    # if we found a msgstr before msgid, this is not a good structure
                    return (True,
                    "Erreur : msgstr trouvé avant msgid")

                msgstr_text = []
                msgstr_text.append(line[6:].strip())
                i = 1
                if (pos + i) < len(data[1:]):
                    next_line = data[1:][pos + i]
                else:
                    next_line = ""

                while next_line.startswith('"'):
                    msgstr_text.append(next_line.strip())
                    i += 1
                    if (pos + i) < len(data[1:]):
                        next_line = data[1:][pos + i]
                    else:
                        next_line = ""
                    

            elif line.startswith('#: model:') or line.startswith("#: code:") or line.startswith('#, python-format') or line.startswith('#: '):
                supported_lines.append(line.strip())

            
            elif line.startswith('"'):
                # if the line begins with this part, then it means it is a part of msgid or msgstr
                pass

            else:
                return ('true', 'Erreur : ligne "{}" non reconnue'.format(line.strip()))
        
        if (not msgid_text) or (not msgstr_text):
            # if we found partially (or not at all) informations about msgid and msgstr
            # we raise error
            return (True,
            "Erreur : msgstr et/ou msgid non trouvé dans le bloc")

        # now we will find informations about lines (line type, instance to translate, etc...)
        TranslationBlock = apps.get_model('translations', 'TranslationBlock')
        supported_lines_parsed = TranslationBlock.find_lines_infos(supported_lines)
        
        return (False,
        {"block": "\n".join(data),
        "msgid": "\n".join(msgid_text) if isinstance(msgid_text, list) else msgid_text,
        "msgstr": "\n".join(msgstr_text) if isinstance(msgstr_text, list) else msgstr_text,
        "supported_lines": supported_lines_parsed
        })


            



class LineType(models.Model):
    """
    These model defines the type of translation line. It indicates 
    what is the attribute of the instance the line translates.

    The current types are the folowing :
    - field_description
    - help
    - name
    - code_line
    - arch_db
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
    - ir.model
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
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="instances",
        null=False,
        blank=False
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

    def analyze_infos(self, data):
        InstanceType = apps.get_model('translations', 'InstanceType')
        Instance = apps.get_model('translations', 'Instance')
        LineType = apps.get_model('translations', 'LineType')
        self.in_translation_file = True
        if data['instance']:
            # first we check if an instance type exists, else we raise error
            instance_type_name = data['instance']['type']
            instance_type = InstanceType.objects.filter(
                name=instance_type_name)
            if len(instance_type) != 1:
                raise ValueError
            # then if instance type exists, we will check if an instance
            # of this type already exists, else we create it
            instance_name = data['instance']['name']
            line_type_value =  data['line_type']
            instance_line_type = LineType.objects.get(name=line_type_value)
            
            instance_name_parts = instance_name.split('.')
            if len(instance_name_parts) != 2 and instance_type_name != 'module':
                # we have to get module name and instance name
                # but for a module line, it doesn't matter
                raise ValueError

            module_instance_type = InstanceType.objects.get(name='module')
            model_instance_type = InstanceType.objects.get(name='ir.model')
            field_instance_type = InstanceType.objects.get(name='ir.model.fields')
            
            if instance_type_name == 'ir.model.fields':
                if not instance_name_parts[1].startswith('field_'):
                    raise ValueError
                model_field_name = instance_name_parts[1][6:]
                # now we have to find the model inside the field
                found = False
                model_field_parts = model_field_name.split('_')
                module_instance = Instance.objects.filter(name=instance_name_parts[0],
                                                        instance_type=module_instance_type)

                while found == False and len(model_field_parts) >= 1:
                    
                    model_instance = Instance.objects.filter(name="_".join(model_field_parts),
                                            instance_type=model_instance_type)
                    
                    if len(model_instance) == 1:
                        model_instance = model_instance[0]
                        found = True
                    else:
                        model_field_parts.pop()
                
                if found == False:
                    print(model_field_name)
                    raise ValueError

                field_name = model_field_name.replace("_".join(model_field_parts), "", 1)
                if field_name.startswith("_"):
                    field_name = field_name[1:]

                field_instance = Instance.objects.filter(name=field_name,
                                            instance_type=field_instance_type,
                                            parent=model_instance)
                if len(field_instance) == 1:
                    field_instance = field_instance[0]
                else:
                    field_instance = Instance.objects.create(
                        name=field_name,
                        instance_type=field_instance_type,
                        parent=model_instance,
                        project=self.block.file.project
                    )
                self.instance = field_instance
                self.line_type = instance_line_type
            
            elif instance_type_name == "ir.model":
                if not instance_name_parts[1].startswith('model_'):
                    raise ValueError
                    
                model_name = instance_name_parts[1][6:]
                model_instance = Instance.objects.filter(name=model_name,
                                            instance_type=model_instance_type)
                if len(model_instance) == 1:
                    model_instance = model_instance[0]
                else:
                    model_instance = Instance.objects.create(
                        name=model_name,
                        instance_type=model_instance_type,
                        project=self.block.file.project
                    )
                self.instance = model_instance
                self.line_type = instance_line_type
            
            elif instance_type_name == "module":
                module_instance = Instance.objects.filter(name=instance_name_parts[0],
                                                            instance_type=module_instance_type)
                if len(module_instance) == 1:
                    module_instance = module_instance[0]
                else:
                    module_instance = Instance.objects.create(
                        name=instance_name_parts[0],
                        instance_type=module_instance_type,
                        project=self.block.file.project
                    )
                
                self.instance = module_instance
                self.line_type = instance_line_type
        
        self.save()






            

