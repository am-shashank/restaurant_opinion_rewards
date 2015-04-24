# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20150417_2029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refers',
            name='referee_telephone',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(max_length=20, unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='telephone',
            field=models.CharField(max_length=20, unique=True, null=True, blank=True),
        ),
    ]
