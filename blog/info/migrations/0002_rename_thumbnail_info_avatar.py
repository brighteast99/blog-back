# Generated by Django 5.0.2 on 2024-05-06 13:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='info',
            old_name='thumbnail',
            new_name='avatar',
        ),
    ]
