# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-05 22:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0006_failure'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='fail_status',
        ),
    ]
