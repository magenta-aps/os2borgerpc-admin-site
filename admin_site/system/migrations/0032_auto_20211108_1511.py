# Generated by Django 3.1.9 on 2021-11-08 15:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system", "0031_auto_20211029_1102"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ciceropatron",
            name="patron_id",
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
