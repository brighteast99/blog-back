# Generated by Django 5.0.7 on 2024-08-16 08:46

import blog.storage
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0021_draft_text_content_template_text_content"),
        ("media", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="draft",
            name="thumbnail",
        ),
        migrations.RemoveField(
            model_name="post",
            name="thumbnail",
        ),
        migrations.RemoveField(
            model_name="template",
            name="thumbnail",
        ),
        migrations.AlterField(
            model_name="category",
            name="cover_image",
            field=models.ImageField(
                blank=True,
                null=True,
                storage=blog.storage.Cafe24OBS,
                upload_to="category-images/",
            ),
        ),
        migrations.AlterField(
            model_name="draft",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)ss",
                to="core.category",
            ),
        ),
        migrations.RemoveField(
            model_name="draft",
            name="images",
        ),
        migrations.AlterField(
            model_name="post",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)ss",
                to="core.category",
            ),
        ),
        migrations.RemoveField(
            model_name="post",
            name="images",
        ),
        migrations.RemoveField(
            model_name="template",
            name="images",
        ),
        migrations.AddField(
            model_name="draft",
            name="images",
            field=models.ManyToManyField(
                related_name="%(class)s_content_of", to="media.image"
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="images",
            field=models.ManyToManyField(
                related_name="%(class)s_content_of", to="media.image"
            ),
        ),
        migrations.AddField(
            model_name="template",
            name="images",
            field=models.ManyToManyField(
                related_name="%(class)s_content_of", to="media.image"
            ),
        ),
    ]