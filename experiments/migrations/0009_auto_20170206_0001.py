# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-06 06:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0008_auto_20170205_2344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phase',
            name='fail_phase',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiments.Phase', verbose_name=b'Phase to redirect to if failed too many times'),
        ),
    ]
