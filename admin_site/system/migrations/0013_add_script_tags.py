# Generated by Django 3.1.4 on 2021-04-08 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0012_script_author'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScriptTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='script',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='scripts', to='system.ScriptTag'),
        ),
    ]
