# Generated by Django 5.1.2 on 2024-10-21 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(default='', upload_to='core/static/img/posts/', verbose_name='Image'),
            preserve_default=False,
        ),
    ]
