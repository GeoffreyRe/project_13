from django.core.management.base import BaseCommand
from translations.models import InstanceType, LineType
from projects.models import Role


class Command(BaseCommand):
    help = 'Append required line type and instance type to database'

    def handle(self, *args, **options):
        types = {'lines': ['field_description', 'name', 'help', 'code', 'other', 'arch_db'],
                 'instances': ['module', 'ir.model', 'ir.ui.view', 'ir.ui.menu',
                               'ir.actions.act_window', 'other', 'ir.model.fields',
                               'code', 'code.position'],
                 'user_role': ['DEV', 'TRA']}
        create = False
        for line_type in types['lines']:
            line_obj = LineType.objects.filter(name=line_type)
            if not line_obj:
                create = True
                LineType.objects.create(name=line_type)

        for instance_type in types['instances']:
            instance_obj = InstanceType.objects.filter(name=instance_type)
            if not instance_obj:
                create = True
                InstanceType.objects.create(name=instance_type)

        for role in types['user_role']:
            Role.objects.get_or_create(name=role)

        if create:
            self.stdout.write(self.style.SUCCESS('Command executed with success'))
        else:
            self.stdout.write(self.style.WARNING('Command executed but nothing has been created'))
