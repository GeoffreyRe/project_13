# Generated by Django 3.1.1 on 2020-09-16 14:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('translations', '0005_auto_20200910_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instance',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='instance_childs', to='translations.instance'),
        ),
    ]
