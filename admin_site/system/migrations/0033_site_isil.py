# Generated by Django 3.1.9 on 2021-11-09 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0032_auto_20211108_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='isil',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='ISIL'),
        ),
    ]
