# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-07-02 11:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_auto_20160702_0847'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='event_open',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='event_video_open',
        ),
    ]
