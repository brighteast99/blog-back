# Generated by Django 5.0.2 on 2024-02-18 18:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_rename_date_created_post_created_at_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="category",
            name="parent",
        ),
        migrations.AddField(
            model_name="category",
            name="subcategory_of",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subcategories",
                to="core.category",
            ),
        ),
    ]
