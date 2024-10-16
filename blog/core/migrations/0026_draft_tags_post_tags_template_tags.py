# Generated by Django 5.1.2 on 2024-10-16 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0025_alter_draft_options_draft_updated_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="draft",
            name="tags",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="post",
            name="tags",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="template",
            name="tags",
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
