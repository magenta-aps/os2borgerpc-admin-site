# Generated by Django 3.2.9 on 2022-02-04 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0040_alter_imageversion_platform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageversion',
            name='release_notes',
            field=models.TextField(max_length=1500),
        ),
    ]
