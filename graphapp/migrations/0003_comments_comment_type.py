# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-01-14 15:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graphapp', '0002_auto_20170114_0211'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='comment_type',
            field=models.TextField(null=True),
        ),
    ]