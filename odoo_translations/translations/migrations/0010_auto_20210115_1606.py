# Generated by Django 3.1.1 on 2021-01-15 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translations', '0009_instance_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instance',
            name='name',
            field=models.CharField(max_length=300),
        ),
    ]
