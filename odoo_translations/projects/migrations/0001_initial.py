# Generated by Django 3.1.1 on 2020-09-03 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('DEV', 'Développeur'), ('TRA', 'Traducteur')], max_length=3, verbose_name='Nom du rôle')),
            ],
        ),
    ]
