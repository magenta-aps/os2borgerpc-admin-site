# Generated by Django 4.2.15 on 2024-09-10 11:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("system", "0089_alter_wakeweekplan_sleep_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="pc",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="system.product",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="config_name",
            field=models.CharField(
                max_length=40, null=True, verbose_name="config name"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="short_name",
            field=models.CharField(max_length=20, null=True, verbose_name="short name"),
        ),
    ]
