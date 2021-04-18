from django.db import models


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

    class Meta:
        # rename table created by django in db
        db_table = "line_type"


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
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return "type d'instance : {}".format(self.name)

    class Meta:
        # rename table created by django in db
        db_table = "instance_type"
