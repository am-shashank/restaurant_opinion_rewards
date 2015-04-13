# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20150413_0335'),
    ]

    operations = [
        migrations.CreateModel(
            name='Friends',
            fields=[
                ('user_id', models.ForeignKey(primary_key=True, db_column='user_id', to='app.User')),
                ('friend_id', models.ForeignKey(related_name='Friends_friend_id', primary_key=True, db_column='friend_id', serialize=False, to='app.User')),
            ],
            options={
                'db_table': 'Friends',
            },
        ),
    ]
