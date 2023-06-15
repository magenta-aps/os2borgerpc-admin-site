# Generated by Django 3.2.12 on 2022-06-29 09:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system", "0055_alter_input_value_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pc",
            name="uid",
            field=models.CharField(
                db_index=True, max_length=255, unique=True, verbose_name="UID"
            ),
        ),
    ]
