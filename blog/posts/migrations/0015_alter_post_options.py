# Generated by Django 5.0.2 on 2024-05-17 19:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_post_images'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-created_at']},
        ),
    ]
