from django.db import models

# Create your models here.
class TranslationFile(models.Model):
    """
    This model represents project's translation files.
    """
    # file name of file.
    # by default, if will be the name of the original file but it can be changed
    name = models.CharField(max_length=40, null=False, blank=False)
    is_template = models.BooleanField(default=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name="tranlation_files",
        null=False
    )
    # the language that the file translates. If template, can be null.
    translated_language = models.CharField(max_length=40, null=True)

    def get_file_location(instance, filename):
        """
        This method returns the location where the file must be located.
        instance : instance of the translation_file
        filename : the name of the file that has been uploaded
        """
        project_directory_name = str(instance.project.id) + "_" + instance.project.name
        # the file must have .pot if it is a template file
        # for a regular file, is 
        extension = ".pot" if instance.is_template == True else ".po"
        file_name = instance.translated_language if not instance.is_template else "template"
        complete_name = file_name + extension
        return "translation_files/{0}/{1}".format(project_directory_name, complete_name)

    # file wich will be uploaded
    original_file = models.FileField(upload_to=get_file_location, null=False)

    def __str__(self):
        return "fichier de traduction : {}".format(self.name)

class TranslationBlock(models.Model):
    file = models.ForeignKey(TranslationFile,
                            on_delete=models.CASCADE,
                            null=False,
                            related_name="translation_blocks")
    original_text = models.TextField(null=False, blank=False)
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
                            null=True
                            )
    def __str__(self):
        sentence = "instance {} de type {}".format(self.name, self.instance_type.name)

class TranslationLine(models.Model):
    block = models.ForeignKey(TranslationBlock,
                            on_delete=models.CASCADE,
                            related_name="translation_lines")
    in_translation_file = models.BooleanField(null=False)
    in_template_file = models.BooleanField(null=False)
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

