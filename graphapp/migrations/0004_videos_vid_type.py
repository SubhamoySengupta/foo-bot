# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-01-14 20:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graphapp', '0003_comments_comment_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='videos',
            name='vid_type',
            field=models.TextField(default='video'),
        ),
    ]
