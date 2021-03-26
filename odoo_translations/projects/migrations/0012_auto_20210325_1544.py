# Generated by Django 3.1.1 on 2021-03-25 14:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_remove_project_template_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userproject',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_on_project', to='projects.project'),
        ),
    ]