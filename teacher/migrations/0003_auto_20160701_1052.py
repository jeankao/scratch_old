# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-07-01 02:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0002_auto_20160618_0727'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='group_show_size',
            field=models.IntegerField(default=2),
        ),
        migrations.AddField(
            model_name='classroom',
            name='group_size',
            field=models.IntegerField(default=4),
        ),
    ]
