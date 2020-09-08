# Generated by Django 3.1.1 on 2020-09-08 13:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('translations', '0001_initial'),
        ('projects', '0007_auto_20200904_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='template_file',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='project_where_template', to='translations.translationfile'),
        ),
    ]