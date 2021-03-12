from django.db import models
from django.apps import apps
from translations.exceptions import NoTranslationFoundInFileError, NoOdooTranslationFileHeader, TranslationBlockStructureNotGoodError


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
    name = models.CharField(max_length=300, null=False, blank=False)
    instance_type = models.ForeignKey(
                                    'translations.InstanceType',
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
    
    def get_number_of_translations(self, lang='fr'):
        blocks_list = self.project.translation_files.filter(translated_language=lang).values_list('translation_blocks', flat=True)
        total_translations = len(apps.get_model('translations.TranslationLine').objects.filter(instance=self, block__in=blocks_list)) + \
            len(apps.get_model('translations.TranslationLine').objects.filter(instance__in=self.instance_childs.all(), block__in=blocks_list))
        return total_translations