# Generated by Django 5.0.2 on 2024-05-17 19:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0016_draft"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Draft",
            new_name="Template",
        ),
    ]
