# Generated by Django 5.1.2 on 2024-10-24 18:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0002_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='like',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='likes', to='twitter.post'),
        ),
    ]
