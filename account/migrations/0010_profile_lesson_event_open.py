# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-07-02 00:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_auto_20160630_1207'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='lesson_event_open',
            field=models.BooleanField(default=True),
        ),
    ]