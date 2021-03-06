# Generated by Django 3.1.1 on 2020-10-07 10:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_auto_20200910_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='creation_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de création'),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=40, verbose_name='Nom du projet'),
        ),
    ]
