# Generated by Django 3.1.1 on 2020-09-03 15:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_project'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='Description du projet',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='Nom du projet',
            new_name='name',
        ),
    ]