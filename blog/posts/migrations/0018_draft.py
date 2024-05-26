# Generated by Django 5.0.2 on 2024-05-21 14:39

import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_rename_draft_template'),
    ]

    operations = [
        migrations.CreateModel(
            name='Draft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(blank=True, null=True)),
                ('thumbnail', models.URLField(blank=True, null=True)),
                ('images', django.contrib.postgres.fields.ArrayField(base_field=models.URLField(), default=list, size=None)),
                ('title', models.CharField(max_length=100)),
                ('is_hidden', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='drafts', to='posts.category')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
