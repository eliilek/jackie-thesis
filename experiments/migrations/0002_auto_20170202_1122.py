# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-02 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='training',
        ),
        migrations.AddField(
            model_name='phase',
            name='feedback',
            field=models.BooleanField(default=True),
        ),
    ]