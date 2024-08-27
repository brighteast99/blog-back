# Generated by Django 5.0.7 on 2024-08-16 08:28

import blog.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Image",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "file",
                    models.ImageField(
                        storage=blog.storage.Cafe24OBS, unique=True, upload_to="media/"
                    ),
                ),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-uploaded_at"],
            },
        ),
    ]