# Generated by Django 5.0.2 on 2024-03-23 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_category_is_hidden'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='cover_image',
            field=models.URLField(blank=True, null=True),
        ),
    ]