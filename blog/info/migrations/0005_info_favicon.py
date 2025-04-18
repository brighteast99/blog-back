# Generated by Django 5.0.7 on 2024-08-06 16:13

from django.db import migrations, models

import blog.storage


class Migration(migrations.Migration):

    dependencies = [
        ("info", "0004_alter_info_avatar"),
    ]

    operations = [
        migrations.AddField(
            model_name="info",
            name="favicon",
            field=models.ImageField(
                blank=True,
                null=True,
                storage=blog.storage.OverwriteOBS,
                upload_to="staticfiles/",
            ),
        ),
    ]
