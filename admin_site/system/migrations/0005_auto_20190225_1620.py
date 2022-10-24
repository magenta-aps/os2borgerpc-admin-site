# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-02-25 16:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import system.models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0004_auto_20180607_1325'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssociatedScript',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField(verbose_name='position')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='policy', to='system.PCGroup')),
                ('script', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='associations', to='system.Script')),
            ],
        ),
        migrations.CreateModel(
            name='AssociatedScriptParameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('string_value', models.CharField(blank=True, max_length=4096, null=True)),
                ('file_value', models.FileField(blank=True, null=True, upload_to=system.models.upload_file_name)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RenameModel(
            old_name='Parameter',
            new_name='BatchParameter',
        ),
        migrations.AlterUniqueTogether(
            name='input',
            unique_together=set([('position', 'script')]),
        ),
        migrations.AddField(
            model_name='associatedscriptparameter',
            name='input',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.Input'),
        ),
        migrations.AddField(
            model_name='associatedscriptparameter',
            name='script',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameters', to='system.AssociatedScript'),
        ),
        migrations.AlterUniqueTogether(
            name='associatedscript',
            unique_together=set([('position', 'group')]),
        ),
    ]
