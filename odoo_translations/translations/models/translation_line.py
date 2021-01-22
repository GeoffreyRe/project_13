from django.db import models
from django.apps import apps
from translations.exceptions import NoTranslationFoundInFileError, NoOdooTranslationFileHeader, TranslationBlockStructureNotGoodError


class TranslationLine(models.Model):
    block = models.ForeignKey('translations.TranslationBlock',
                            on_delete=models.CASCADE,
                            related_name="translation_lines")
    in_translation_file = models.BooleanField(null=False)
    in_template_file = models.BooleanField(null=True)
    line_type = models.ForeignKey(
                                'translations.LineType',
                                on_delete=models.PROTECT,
                                related_name="translation_lines",
                                null=False
                                )
    instance = models.ForeignKey(
        'translations.Instance',
        on_delete=models.PROTECT,
        blank=False,
        null=False
        )
    
    def __str__(self):
        return "ligne de traduction numéro {}".format(self.id)

    def find_or_create_instance(self, name, instance_type, instance_line_type):
        Instance = apps.get_model('translations', 'Instance')
        instance = Instance.objects.filter(name=name,
                                            instance_type=instance_type)       
        if len(instance) == 1:
            instance = instance[0]
        else:
            instance = Instance.objects.create(
                name=name,
                instance_type= instance_type,
                project=self.block.file.project
            )

        self.instance = instance
        self.line_type = instance_line_type

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
            
            instance_name_parts = instance_name.split('.') if instance_type_name != "code" else instance_name.split(':')
            if len(instance_name_parts) != 2 and instance_type_name != 'module':
                # we have to get module name and instance name
                # but for a module line, it doesn't matter
                raise ValueError

            module_instance_type = InstanceType.objects.get(name='module')
            model_instance_type = InstanceType.objects.get(name='ir.model')
            field_instance_type = InstanceType.objects.get(name='ir.model.fields')
            view_instance_type = InstanceType.objects.get(name='ir.ui.view')
            actwindow_instance_type = InstanceType.objects.get(name='ir.actions.act_window')
            menu_instance_type = InstanceType.objects.get(name='ir.ui.menu')
            code_instance_type = InstanceType.objects.get(name='code')
            code_pos_instance_type = InstanceType.objects.get(name='code.position')
            
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

                self.find_or_create_instance(instance_name_parts[1][6:], model_instance_type, instance_line_type)
            
            elif instance_type_name == "module":
                self.find_or_create_instance(instance_name_parts[0], module_instance_type, instance_line_type)
            
            elif instance_type_name == "ir.ui.view":
                self.find_or_create_instance(instance_name_parts[1], view_instance_type, instance_line_type)
            
            elif instance_type_name == "ir.actions.act_window":
                self.find_or_create_instance(instance_name_parts[1], actwindow_instance_type, instance_line_type)
                
            
            elif instance_type_name == "ir.ui.menu":
                self.find_or_create_instance(instance_name_parts[1], menu_instance_type, instance_line_type)
            
            elif instance_type_name == "code":
                # TODO: Try to integrate this part inside find_or_create_instance function
                code_instance = Instance.objects.filter(name=instance_name_parts[0],
                                                            instance_type=code_instance_type)
                
                if len(code_instance) == 1:
                    code_instance = code_instance[0]
                else:
                    code_instance = Instance.objects.create(
                        name=instance_name_parts[0],
                        instance_type= code_instance_type,
                        project=self.block.file.project
                    )

                code_pos_instance = Instance.objects.filter(name=instance_name_parts[1],
                                                            instance_type=code_pos_instance_type,
                                                            parent=code_instance)
                if len(code_pos_instance) == 1:
                    code_pos_instance = code_pos_instance[0]
                else:
                    code_pos_instance = Instance.objects.create(
                        name=instance_name_parts[1],
                        instance_type= code_pos_instance_type,
                        project=self.block.file.project,
                        parent=code_instance
                    )
                  
                self.instance = code_pos_instance
                self.line_type = instance_line_type
        else:
            # if instance is False, it means that the line is unkown
            other_instance_type = InstanceType.objects.get(name="other")
            other_line_type = LineType.objects.get(name="other")
            other_instance, created = Instance.objects.get_or_create(
                name=data['line'],
                instance_type=other_instance_type,
                project=self.block.file.project
                )
            self.instance = other_instance
            self.line_type = other_line_type
                

        
        self.save()
    
    class Meta:
        # rename table created by django in db
        db_table="translation_line"