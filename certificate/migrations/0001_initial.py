# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-06-12 06:28
from __future__ import unicode_literals

import certificate.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(default=b'/static/certificate/null.jpg', upload_to=certificate.models.upload_path_handler)),
                ('student_id', models.IntegerField(default=0)),
                ('publish', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]