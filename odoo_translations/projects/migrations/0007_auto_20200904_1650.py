# Generated by Django 3.1.1 on 2020-09-04 14:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0006_invitation_userproject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='accepted',
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects_created', to=settings.AUTH_USER_MODEL),
        ),
    ]
