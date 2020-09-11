# Generated by Django 3.1.1 on 2020-09-10 10:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('translations', '0002_translationline_instance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='translationline',
            name='instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='translations.instance'),
        ),
    ]