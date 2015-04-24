# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20150417_2026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refers',
            name='referee_telephone',
            field=models.ForeignKey(primary_key=True, db_column='referee_telephone', to='app.User'),
        ),
        migrations.AlterField(
            model_name='refers',
            name='restaurant_id',
            field=models.ForeignKey(primary_key=True, db_column='restaurant_id', serialize=False, to='app.Restaurant'),
        ),
    ]
