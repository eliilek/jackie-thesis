# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-02 20:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0002_auto_20170202_1122'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
