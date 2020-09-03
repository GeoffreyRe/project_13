# Generated by Django 3.1.1 on 2020-09-03 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(choices=[('DEV', 'Développeur'), ('TRA', 'Traducteur')], max_length=3, unique=True, verbose_name='Nom du rôle'),
        ),
    ]
