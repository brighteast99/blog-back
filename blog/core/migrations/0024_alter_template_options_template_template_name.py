# Generated by Django 5.0.7 on 2024-09-06 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0023_draft_thumbnail_post_thumbnail_template_thumbnail"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="template",
            options={"ordering": ["template_name"]},
        ),
        migrations.AddField(
            model_name="template",
            name="template_name",
            field=models.CharField(default="이름 없는 템플릿", max_length=100),
            preserve_default=False,
        ),
    ]
