# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-06-30 04:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_visitorlog_ip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitorlog',
            name='IP',
            field=models.CharField(default=b'', max_length=20),
        ),
    ]
