# Generated by Django 4.2.1 on 2023-06-29 16:28

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("system", "0069_pcgroup_supervisors"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pc",
            name="is_update_required",
        ),
    ]
