# Generated by Django 5.0.2 on 2024-07-30 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0020_alter_template_options_rename_name_template_title_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="draft",
            name="text_content",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="template",
            name="text_content",
            field=models.TextField(blank=True, null=True),
        ),
    ]
